import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.prompts.templates import get_rule_error_detection_prompt
from src.utils.helpers import generate_text, get_provider


def generate_with_retry(prompt, provider, base_delay=5, retry_delay=15):
    """
    Retry wrapper for API calls.
    Gemini free tier may hit 429 limits, so we wait and retry.
    """
    if provider == "gemini":
        time.sleep(base_delay)

    while True:
        try:
            return generate_text(prompt)
        except Exception as e:
            msg = str(e)
            if provider == "gemini" and ("429" in msg or "RESOURCE_EXHAUSTED" in msg):
                print(f"Rate limit hit. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise


def main():
    provider = get_provider()

    broken_rules_path = ROOT / "data" / "processed" / "broken_tic_tac_toe.txt"

    if not broken_rules_path.exists():
        raise FileNotFoundError(
            f"Broken rules file not found: {broken_rules_path}"
        )

    broken_rules = broken_rules_path.read_text(encoding="utf-8")

    prompt = get_rule_error_detection_prompt(broken_rules)
    response = generate_with_retry(prompt, provider)

    print("\nBROKEN RULES\n")
    print(broken_rules)

    print("\n" + "=" * 60 + "\n")

    print("MODEL RESPONSE\n")
    print(response)

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / f"rule_error_detection_{provider}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("BROKEN RULES\n\n")
        f.write(broken_rules)
        f.write("\n\n" + "=" * 60 + "\n\n")
        f.write("PROMPT\n\n")
        f.write(prompt)
        f.write("\n\n" + "=" * 60 + "\n\n")
        f.write("MODEL RESPONSE\n\n")
        f.write(response)

    print("\nSaved results to:", output_path)


if __name__ == "__main__":
    main()

