import json
from pathlib import Path
import pandas as pd

from src.evaluation.generation_metrics import evaluate_generated_game
from src.evaluation.rule_metrics import score_error_detection, score_rule_summary

BASE_DIR = Path(__file__).resolve().parents[2]
RESPONSES_DIR = BASE_DIR / "results" / "responses"
OUTPUT_DIR = BASE_DIR / "results" / "tables"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GAME_CONFIG = {
    "tictactoe": {
        "schema": "data/processed/tictactoe/rule_schema_tictactoe.json",
    },
    "connect_four": {
        "schema": "data/processed/connect_four/rule_schema_connectfour.json",
    },
}

def load_text(path):
    return Path(path).read_text(encoding="utf-8")

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def detect_game(filename: str):
    name = filename.lower()
    if "tictactoe" in name:
        return "tictactoe"
    if "connect_four" in name or "connectfour" in name:
        return "connect_four"
    raise ValueError(f"Unknown game: {filename}")

def detect_model(filename: str):
    name = filename.lower()
    if "llama" in name:
        return "llama"
    if "qwen" in name:
        return "qwen"
    return "unknown"

# --- EVALUATION FUNCTIONS ---

def evaluate_rule_understanding():
    """Processes files and saves results to results/responses/rule_understanding/"""
    rows = []
    target_dir = RESPONSES_DIR / "rule_understanding"
    files = list(target_dir.glob("*.txt"))
    
    if not files:
        print(f"⚠️ Warning: No files found in {target_dir}")
        return

    for file in files:
        print(f"Processing Rule Understanding: {file.name}")
        text = load_text(file)
        game = detect_game(file.name)
        model = detect_model(file.name)

        schema_path = BASE_DIR / GAME_CONFIG[game]["schema"]
        schema = load_json(schema_path)
        score = score_rule_summary(text, schema)

        rows.append({
            "model": model,
            "game": game,
            "completeness": score["completeness"],
            "precision": score.get("precision", None),
            "f1": score.get("f1", None),
            "correct_items": score.get("correct_items", None),
            "filled_items": score.get("filled_items", None),
            "total_items": score["total_items"],
            "missing_items": ", ".join(score.get("missing_items", [])),
            "incorrect_items": ", ".join(score.get("incorrect_items", [])),
            "hallucinated_items": ", ".join(score.get("hallucinated_items", [])),
        })

    df = pd.DataFrame(rows)
    # Save to rule_understanding folder
    df.to_csv(target_dir / "rule_understanding_results.csv", index=False)
    print(f" ✅ Saved rule understanding results to {target_dir}")

def evaluate_rule_errors():
    """Processes files and saves results to results/responses/rule_error_detection/"""
    rows = []
    target_dir = RESPONSES_DIR / "rule_error_detection"
    
    case_files = {
        "tictactoe": BASE_DIR / "data" / "processed" / "tictactoe" / "rule_error_cases_tictactoe.json",
        "connect_four": BASE_DIR / "data" / "processed" / "connect_four" / "rule_error_cases_connect_four.json",
    }

    files = list(target_dir.glob("*.txt"))
    if not files:
        print(f" ⚠️ Warning: No files found in {target_dir}")
        return

    for game, case_file in case_files.items():
        cases = load_json(case_file)
        case_map = {case["id"]: case["gold_errors"] for case in cases}

        for file in files:
            if game not in file.name.lower():
                continue

            model = detect_model(file.name)
            text = load_text(file)

            matched_case_id = None
            for case_id in case_map.keys():
                if file.stem.endswith(case_id):
                    matched_case_id = case_id
                    break

            if matched_case_id:
                print(f"Processing Error Detection: {file.name}")
                gold = case_map[matched_case_id]
                score = score_error_detection(text, gold)

                rows.append({
                    "model": model,
                    "game": game,
                    "case_id": matched_case_id,
                    "precision": score["precision"],
                    "recall": score["recall"],
                    "f1": score["f1"],
                })

    if rows:
        df = pd.DataFrame(rows)
        summary = (
            df.groupby(["model", "game"], as_index=False)
            .agg(
                num_cases=("case_id", "count"),
                precision=("precision", "mean"),
                recall=("recall", "mean"),
                f1=("f1", "mean"),
            )
        )
        summary = summary.round(4)
        # Save to rule_error_detection folder
        summary.to_csv(target_dir / "rule_error_results.csv", index=False)
        print(f" ✅ Saved rule error detection results to {target_dir}")

def evaluate_generation():
    """Processes files and saves results to results/responses/game_generation/"""
    rows = []
    target_dir = RESPONSES_DIR / "game_generation"
    files = list(target_dir.glob("*.txt"))

    if not files:
        print(f" ⚠️ Warning: No files found in {target_dir}")
        return

    for file in files:
        print(f"Processing Generation: {file.name}")
        text = load_text(file)
        model = detect_model(file.name)
        score = evaluate_generated_game(text)

        rows.append({
            "model": model,
            "clarity": score["clarity"],
            "consistency": score["internal_consistency"],
            "balance": score["balance"],
            "fun": score["fun_factor"],
            "coverage": score["section_coverage"],
            "playable": score.get("playable", None),
        })

    df = pd.DataFrame(rows)
    # Save to game_generation folder
    df.to_csv(target_dir / "generation_results.csv", index=False)
    print(f" ✅ Saved generation results to {target_dir}")

if __name__ == "__main__":
    evaluate_rule_understanding()
    evaluate_rule_errors()
    evaluate_generation()
    print("\n🚀 All evaluation complete")