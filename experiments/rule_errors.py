import sys
import os
from pathlib import Path

# -------------------------------------------------
# Setup project root so src imports work
# -------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -------------------------------------------------
# Imports
# -------------------------------------------------
from src.prompts.templates import get_rule_error_detection_prompt
from src.utils.helpers import generate_text


def main():

    # -------------------------------------------------
    # Locate broken rules file
    # -------------------------------------------------
    broken_rules_path = ROOT / "data" / "processed" / "tictactoe_rules_broken.txt"

    if not broken_rules_path.exists():
        raise FileNotFoundError(
            f"Broken rule file not found at: {broken_rules_path}"
        )

    # -------------------------------------------------
    # Load broken rules
    # -------------------------------------------------
    with open(broken_rules_path, "r", encoding="utf-8") as f:
        broken_rules = f.read()

    # -------------------------------------------------
    # Build prompt
    # -------------------------------------------------
    prompt = get_rule_error_detection_prompt(broken_rules)

    # -------------------------------------------------
    # Call LLM
    # -------------------------------------------------
    response = generate_text(prompt)

    # -------------------------------------------------
    # Print results
    # -------------------------------------------------
    print("\nBROKEN RULES\n")
    print(broken_rules)

    print("\n" + "=" * 60 + "\n")

    print("MODEL RESPONSE\n")
    print(response)

    # -------------------------------------------------
    # Save results
    # -------------------------------------------------
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / "rule_error_detection.txt"

    with open(output_path, "w", encoding="utf-8") as f:

        f.write("BROKEN RULES\n")
        f.write(broken_rules)

        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("PROMPT\n")
        f.write(prompt)

        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("MODEL RESPONSE\n")
        f.write(response)

    print("\nSaved results to:", output_path)


if __name__ == "__main__":
    main()