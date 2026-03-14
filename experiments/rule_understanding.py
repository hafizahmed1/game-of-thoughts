import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.pipelines.rule_understanding import prepare_tictactoe_rule_understanding
from src.utils.helpers import generate_text
from src.utils.rule_scorer import score_tictactoe_rules

def main():
    exp = prepare_tictactoe_rule_understanding()

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"
    tables_dir = ROOT / "results" / "tables"

    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    for condition, prompt in exp["prompts"].items():

        print(f"Running: {condition}")

        response = generate_text(prompt)

        metrics = score_tictactoe_rules(response)

        summary_rows.append({
            "condition": condition,
            "rule_completeness_score": metrics["rule_completeness_score"],
            "invented_rules": 0,
            "missed_constraints": metrics["missed_constraints"],
            "notes": ""
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = tables_dir / "rule_understanding_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    print("Saved:", summary_path)


if __name__ == "__main__":
    main()