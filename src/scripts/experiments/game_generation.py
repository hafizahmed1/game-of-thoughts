import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3] 

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.config import SUPPORTED_MODELS
from src.prompts.prompt_builder import build_game_generation_prompt
from src.llm.model_loader import load_model


def safe_filename(text: str) -> str:
    return text.replace("/", "_").replace("\\", "_").replace(":", "_")


def main():
    if len(sys.argv) > 1:
        selected_model = sys.argv[1].lower()
    else:
        selected_model = SUPPORTED_MODELS[0]

    safe_model_name = safe_filename(selected_model)

    model = load_model(selected_model)

    theme = "a simple two-player strategy board game about collecting treasure"

    prompt = build_game_generation_prompt(seed_idea=theme)
    response = model.generate(prompt)

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"/"game_generation"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompts_dir / f"game_generation_{safe_model_name}_prompt.txt"
    response_path = responses_dir / f"game_generation_{safe_model_name}.txt"

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