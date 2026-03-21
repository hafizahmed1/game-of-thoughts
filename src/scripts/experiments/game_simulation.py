import sys
import csv
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3] 
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.config import SUPPORTED_MODELS, get_provider
from src.games.registry import get_game
from src.data.generate_cases import generate_cases
from src.pipelines.game_simulation import run_game_simulation
from src.llm.model_loader import load_model

def safe_filename(text: str) -> str:
    return text.replace("/", "_").replace("\\", "_").replace(":", "_")

def load_rules(game_name: str) -> str:
    path = ROOT / "data" / "raw" / game_name / "rules.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_args():
    if "--model" not in sys.argv or "--game" not in sys.argv:
        raise ValueError("Usage: python experiments/game_simulation.py --model <id> --game <name>")
    return sys.argv[sys.argv.index("--model") + 1].lower(), sys.argv[sys.argv.index("--game") + 1]

def write_rows_to_csv(csv_path: Path, rows: list[dict]) -> None:
    if not rows: return
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def append_rows_to_csv(csv_path: Path, rows: list[dict]) -> None:
    if not rows: return
    file_exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists: writer.writeheader()
        writer.writerows(rows)

def main():
    model_name, game_name = parse_args()
    provider = get_provider(model_name)
    safe_model_name = safe_filename(model_name)

    game = get_game(game_name)
    model = load_model(model_name)
    rules_text = load_rules(game_name)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    cases = generate_cases(game=game, num_cases=50, prefix="case", seed=42)

    tables_dir = ROOT / "results" / "tables"
    responses_dir = ROOT / "results" / "responses" / "simulation"
    tables_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    json_output_path = responses_dir / f"{game_name}_{safe_model_name}_trace_{run_id}.json"
    summary_rows = []
    detailed_traces = []

    for case in cases:
        state = game.state_from_dict(case["state"])
        initial_board_text = game.state_to_text(state)

        result = run_game_simulation(
            game=game, rules_text=rules_text, initial_state=state, model=model, max_turns=case["max_turns"]
        )

        # Build Summary Data
        summary_rows.append({
            "run_id": run_id, "case_id": case["id"], "game": game_name, "model": model_name,
            "initial_board": initial_board_text, "stopped_reason": result.stopped_reason,
            "winner": result.winner, "valid_turns": sum(1 for t in result.turns if t.move_valid),
            "total_turns": len(result.turns)
        })

        # Build Detailed GoT Trace
        detailed_traces.append({
            "case_id": case["id"], "model": model_name, "game": game_name,
            "initial_board": initial_board_text, "final_board": result.final_state_text,
            "stopped_reason": result.stopped_reason, "winner": result.winner,
            "turns": [
                {
                    "turn_index": t.turn_index,
                    "player": t.player,
                    "board_state": t.state_text_before,
                    "thought": t.raw_response, # Captures the GoT Reasoning
                    "move": t.parsed_move_text,
                    "move_valid": t.move_valid
                } for t in result.turns
            ]
        })

    write_rows_to_csv(tables_dir / f"{game_name}_{safe_model_name}_results.csv", summary_rows)
    append_rows_to_csv(tables_dir / "all_simulation_results.csv", summary_rows)

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_traces, f, indent=2)

    print(f"✅ Simulation Complete. Trace saved to: {json_output_path}")

if __name__ == "__main__":
    main()