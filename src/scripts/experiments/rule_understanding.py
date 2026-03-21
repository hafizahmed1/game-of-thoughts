import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3] 

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
from src.config import SUPPORTED_MODELS
from src.prompts.prompt_builder import build_rule_understanding_prompt
from src.llm.model_loader import load_model


def safe_filename(text: str) -> str:
    return text.replace("/", "_").replace("\\", "_").replace(":", "_")


def load_rules(game_name: str) -> str:
    path = ROOT / "data" / "raw" / game_name / "rules.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_response(text: str) -> str:
    """
    Clean model output before saving.

    This removes extra whitespace and strips off any reasoning tags
    if a model unexpectedly emits them.
    """
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>")[-1].strip()

    return text


def parse_args():
    if "--model" not in sys.argv or "--game" not in sys.argv:
        raise ValueError(
            f"Usage: python experiments/rule_understanding.py "
            f"--model <{'|'.join(SUPPORTED_MODELS)}> --game <game_name>"
        )

    model_name = sys.argv[sys.argv.index("--model") + 1].lower()
    game_name = sys.argv[sys.argv.index("--game") + 1]
    return model_name, game_name


def main():
    model_name, game_name = parse_args()
    safe_model_name = safe_filename(model_name)

    model = load_model(model_name)
    rules_text = load_rules(game_name)

    prompt = build_rule_understanding_prompt(
        game_name=game_name,
        rules_text=rules_text,
    )

    raw_response = model.generate(prompt)
    response = clean_response(raw_response)

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"/"rule_understanding"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompts_dir / f"rule_understanding_{game_name}_{safe_model_name}_prompt.txt"
    response_path = responses_dir / f"rule_understanding_{game_name}_{safe_model_name}.txt"

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