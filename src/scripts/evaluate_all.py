import json
from pathlib import Path

import pandas as pd

from src.evaluation.generation_metrics import evaluate_generated_game
from src.evaluation.rule_metrics import score_error_detection, score_rule_summary


BASE_DIR = Path(".")
RESPONSES_DIR = BASE_DIR / "results" / "responses"
OUTPUT_DIR = BASE_DIR / "results" / "tables"

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


def evaluate_simulation():
    sim_path = OUTPUT_DIR / "all_simulation_results.csv"
    df = pd.read_csv(sim_path)

    df["case_completed"] = df["stopped_reason"].eq("terminal_state_reached").astype(int)

    df["move_accuracy"] = df.apply(
        lambda r: (r["valid_turns"] / r["total_turns"]) if r["total_turns"] else 0.0,
        axis=1,
    )
    df["invalid_move_rate"] = df.apply(
        lambda r: (r["invalid_turns"] / r["total_turns"]) if r["total_turns"] else 0.0,
        axis=1,
    )

    summary = (
        df.groupby(["game", "model"], as_index=False)
        .agg(
            completion_rate=("case_completed", "mean"),
            move_accuracy=("move_accuracy", "mean"),
            invalid_move_rate=("invalid_move_rate", "mean"),
            avg_turns=("completed_turns", "mean"),
            total_cases=("case_id", "count"),
        )
    )

    for col in ["completion_rate", "move_accuracy", "invalid_move_rate"]:
        summary[col] = summary[col] * 100

    summary = summary.round({
        "completion_rate": 2,
        "move_accuracy": 2,
        "invalid_move_rate": 2,
        "avg_turns": 2,
    })

    summary.to_csv(OUTPUT_DIR / "move_simulation_results.csv", index=False)
    print("Saved move simulation results")


def evaluate_rule_understanding():
    rows = []

    for file in RESPONSES_DIR.glob("rule_understanding_*.txt"):
        text = load_text(file)
        game = detect_game(file.name)
        model = detect_model(file.name)

        schema = load_json(GAME_CONFIG[game]["schema"])
        score = score_rule_summary(text, schema)

        rows.append({
            "model": model,
            "game": game,
            "completeness": score["completeness"],
            "covered_items": score["covered_items"],
            "total_items": score["total_items"],
            "missing_items": ", ".join(score["missing_items"]),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "rule_understanding_results.csv", index=False)
    print("Saved rule understanding results")

def evaluate_rule_errors():
    rows = []

    case_files = {
        "tictactoe": "data/processed/tictactoe/rule_error_cases_tictactoe.json",
        "connect_four": "data/processed/connect_four/rule_error_cases_connect_four.json",
    }

    for game, case_file in case_files.items():
        cases = load_json(case_file)

        if not cases:
            continue

        gold = cases[0]["gold_errors"]

        for file in RESPONSES_DIR.glob(f"rule_error_detection_{game}_*.txt"):
            model = detect_model(file.name)
            text = load_text(file)
            score = score_error_detection(text, gold)

            rows.append({
                "model": model,
                "game": game,
                "precision": score["precision"],
                "recall": score["recall"],
                "f1": score["f1"],
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "rule_error_results.csv", index=False)
    print("Saved rule error detection results")

def evaluate_generation():
    rows = []

    for file in RESPONSES_DIR.glob("game_generation_*.txt"):
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
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "generation_results.csv", index=False)
    print("Saved generation results")


if __name__ == "__main__":
    evaluate_simulation()
    evaluate_rule_understanding()
    evaluate_rule_errors()
    evaluate_generation()
    print("All evaluation complete ✅")