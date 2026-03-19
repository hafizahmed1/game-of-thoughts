from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from src.config import ACTIVE_MODELS, DEFAULT_GAMES


ROOT = Path(__file__).resolve().parent
EXPERIMENTS_DIR = ROOT / "experiments"
TABLES_DIR = ROOT / "results" / "tables"

TABLES_DIR.mkdir(parents=True, exist_ok=True)


EXPERIMENTS = [
    {
        "name": "rule_understanding",
        "script": EXPERIMENTS_DIR / "rule_understanding.py",
        "models": ACTIVE_MODELS,
        "games": DEFAULT_GAMES,
    },
    {
        "name": "game_simulation",
        "script": EXPERIMENTS_DIR / "game_simulation.py",
        "models": ACTIVE_MODELS,
        "games": DEFAULT_GAMES,
    },
    {
        "name": "rule_error_detection",
        "script": EXPERIMENTS_DIR / "rule_error_detection.py",
        "models": ACTIVE_MODELS,
        "games": DEFAULT_GAMES,
    },
    {
        "name": "game_generation",
        "script": EXPERIMENTS_DIR / "game_generation.py",
        "models": ACTIVE_MODELS,
        "games": [None],
    },
]


def build_command(script: Path, experiment_name: str, model: str, game: str | None):
    if experiment_name == "game_generation":
        return [sys.executable, str(script), model]

    return [
        sys.executable,
        str(script),
        "--model",
        model,
        "--game",
        game,
    ]


def run_single_experiment(exp_name, script, model, game):
    command = build_command(script, exp_name, model, game)

    print("\n" + "=" * 70)
    print(f"EXPERIMENT: {exp_name}")
    print(f"MODEL: {model}")
    if game:
        print(f"GAME: {game}")
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print(result.stdout)

    return {
        "experiment": exp_name,
        "game": game if game else "general",
        "model": model,
        "exit_code": result.returncode,
        "status": "success" if result.returncode == 0 else "failed",
    }


def save_summary(rows):
    csv_path = TABLES_DIR / "all_experiments_summary_latest.csv"
    json_path = TABLES_DIR / "all_experiments_summary_latest.json"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["experiment", "game", "model", "exit_code", "status"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print("\nSaved summary CSV:", csv_path)
    print("Saved summary JSON:", json_path)


def main():
    rows = []

    for exp in EXPERIMENTS:
        script = exp["script"]

        if not script.exists():
            print(f"Skipping missing script: {script}")
            continue

        for game in exp["games"]:
            for model in exp["models"]:
                row = run_single_experiment(
                    exp["name"],
                    script,
                    model,
                    game,
                )
                rows.append(row)

    save_summary(rows)

    success = sum(1 for r in rows if r["status"] == "success")
    total = len(rows)

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Successful runs: {success}/{total}")


if __name__ == "__main__":
    main()