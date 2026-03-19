import sys
import csv
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
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
        raise ValueError(
            f"Usage: python experiments/game_simulation.py --model <{'|'.join(SUPPORTED_MODELS)}> --game <game_name>"
        )

    model_name = sys.argv[sys.argv.index("--model") + 1].lower()
    game_name = sys.argv[sys.argv.index("--game") + 1]
    return model_name, game_name


def append_rows_to_csv(csv_path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    file_exists = csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def main():
    model_name, game_name = parse_args()
    provider = get_provider(model_name)
    safe_model_name = safe_filename(model_name)

    game = get_game(game_name)
    model = load_model(model_name)
    rules_text = load_rules(game_name)

    prefix = "ttt_case" if game_name == "tictactoe" else "cf_case"
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    cases = generate_cases(
        game=game,
        num_cases=50,
        prefix=prefix,
        max_turns=game.get_max_moves(),
        seed=42,
    )

    tables_dir = ROOT / "results" / "tables"
    responses_dir = ROOT / "results" / "responses"

    tables_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    pair_master_csv_path = tables_dir / f"{game_name}_{safe_model_name}_simulation_results.csv"
    global_master_csv_path = tables_dir / "all_simulation_results.csv"
    json_output_path = responses_dir / f"{game_name}_{safe_model_name}_simulation_trace_{run_id}.json"

    summary_rows = []
    detailed_rows = []

    for case in cases:
        state = game.state_from_dict(case["state"])
        initial_board_text = game.state_to_text(state)

        result = run_game_simulation(
            game=game,
            rules_text=rules_text,
            initial_state=state,
            model=model,
            max_turns=case["max_turns"],
        )

        row = {
            "run_id": run_id,
            "timestamp": run_id,
            "case_id": case["id"],
            "game": game_name,
            "provider": provider,
            "model": model_name,
            "initial_board": initial_board_text,
            "final_board": result.final_state_text,
            "completed_turns": result.completed_turns,
            "stopped_reason": result.stopped_reason,
            "winner": result.winner,
            "total_turns": len(result.turns),
            "valid_turns": sum(1 for t in result.turns if t.move_valid),
            "invalid_turns": sum(1 for t in result.turns if not t.move_valid),
        }
        summary_rows.append(row)

        detailed_rows.append(
            {
                "run_id": run_id,
                "case_id": case["id"],
                "game": game_name,
                "provider": provider,
                "model": model_name,
                "initial_board": initial_board_text,
                "final_board": result.final_state_text,
                "completed_turns": result.completed_turns,
                "stopped_reason": result.stopped_reason,
                "winner": result.winner,
                "turns": result.to_dict()["turns"],
            }
        )

    append_rows_to_csv(pair_master_csv_path, summary_rows)
    append_rows_to_csv(global_master_csv_path, summary_rows)

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_rows, f, indent=2)

    print(f"Appended pair summary table to: {pair_master_csv_path}")
    print(f"Appended global summary table to: {global_master_csv_path}")
    print(f"Saved detailed board trace to: {json_output_path}")


if __name__ == "__main__":
    main()