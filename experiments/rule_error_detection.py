import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.config import SUPPORTED_MODELS
from src.prompts.prompt_builder import build_rule_error_detection_prompt
from src.llm.model_loader import load_model


def safe_filename(text: str) -> str:
    return text.replace("/", "_").replace("\\", "_").replace(":", "_")


def load_rules(game_name: str) -> tuple[str, str]:
    clean_path = ROOT / "data" / "raw" / game_name / "rules.txt"
    broken_path = ROOT / "data" / "raw" / game_name / "broken_rules.txt"

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_rules = f.read()

    with open(broken_path, "r", encoding="utf-8") as f:
        broken_rules = f.read()

    return clean_rules, broken_rules


def parse_args():
    if "--model" not in sys.argv or "--game" not in sys.argv:
        raise ValueError(
            f"Usage: python experiments/rule_error_detection.py --model <{'|'.join(SUPPORTED_MODELS)}> --game <game_name>"
        )

    model_name = sys.argv[sys.argv.index("--model") + 1].lower()
    game_name = sys.argv[sys.argv.index("--game") + 1]
    return model_name, game_name


def main():
    model_name, game_name = parse_args()
    safe_model_name = safe_filename(model_name)

    model = load_model(model_name)
    clean_rules, broken_rules = load_rules(game_name)

    prompt = build_rule_error_detection_prompt(
        game_name=game_name,
        clean_rules=clean_rules,
        broken_rules=broken_rules,
    )
    response = model.generate(prompt)

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompts_dir / f"rule_error_detection_{game_name}_{safe_model_name}_prompt.txt"
    response_path = responses_dir / f"rule_error_detection_{game_name}_{safe_model_name}.txt"

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    with open(response_path, "w", encoding="utf-8") as f:
        f.write(response)

    print("\nPROMPT\n")
    print(prompt)
    print("\n" + "=" * 60 + "\n")
    print("MODEL RESPONSE\n")
    print(response)
    print(f"\nSaved prompt to: {prompt_path}")
    print(f"Saved response to: {response_path}")


if __name__ == "__main__":
    main()