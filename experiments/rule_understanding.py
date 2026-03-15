import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipelines.rule_understanding import prepare_tictactoe_rule_understanding
from src.utils.helpers import generate_text, get_provider
from src.utils.rule_scorer import score_tictactoe_rules


def main():
    provider = get_provider()

    exp = prepare_tictactoe_rule_understanding()

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"
    tables_dir = ROOT / "results" / "tables"

    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    for condition, prompt in exp["prompts"].items():
        print(f"Running: {condition} [{provider}]")

        response = generate_text(prompt)
        metrics = score_tictactoe_rules(response)

        prompt_path = prompts_dir / f"{condition}_prompt_{provider}.txt"
        response_path = responses_dir / f"{condition}_response_{provider}.txt"

        prompt_path.write_text(prompt, encoding="utf-8")
        response_path.write_text(response, encoding="utf-8")

        summary_rows.append({
            "condition": condition,
            "rule_completeness_score": metrics["rule_completeness_score"],
            "invented_rules": 0,
            "missed_constraints": metrics["missed_constraints"],
            "notes": "",
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = tables_dir / f"rule_understanding_summary_{provider}.csv"
    summary_df.to_csv(summary_path, index=False)

    print("Saved:", summary_path)


if __name__ == "__main__":
    main()