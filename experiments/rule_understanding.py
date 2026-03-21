import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from src.prompts.prompt_builder import build_rule_understanding_prompt
from src.llm.gemini_model import GeminiModel
from src.llm.groq_model import GroqModel

try:
    from google import genai
except ImportError:
    genai = None


def load_model(model_name: str):
    model_name = model_name.lower()

    if model_name == "gemini":
        if genai is None:
            raise ImportError("google-genai is not installed.")

        api_key = os.getenv("GEMINI_API_KEY")
        selected_model = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not selected_model:
            raise ValueError("GEMINI_MODEL not set in .env")

        client = genai.Client(api_key=api_key)
        return GeminiModel(client=client, model_name=selected_model)

    if model_name == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        selected_model = os.getenv("GROQ_MODEL")

        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        if not selected_model:
            raise ValueError("GROQ_MODEL not set in .env")

        return GroqModel(api_key=api_key, model_name=selected_model)

    raise ValueError(f"Unsupported model: {model_name}")


def load_rules(game_name: str) -> str:
    path = ROOT / "data" / "raw" / game_name / "rules.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_args():
    if "--model" not in sys.argv or "--game" not in sys.argv:
        raise ValueError(
            "Usage: python experiments/rule_understanding.py --model <gemini|groq> --game <game_name>"
        )

    model_name = sys.argv[sys.argv.index("--model") + 1]
    game_name = sys.argv[sys.argv.index("--game") + 1]
    return model_name, game_name


def main():
    model_name, game_name = parse_args()

    model = load_model(model_name)
    rules_text = load_rules(game_name)

    prompt = build_rule_understanding_prompt(game_name=game_name, rules_text=rules_text)
    response = model.generate(prompt)

    prompts_dir = ROOT / "results" / "prompts"
    responses_dir = ROOT / "results" / "responses"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompts_dir / f"rule_understanding_{game_name}_{model_name}_prompt.txt"
    response_path = responses_dir / f"rule_understanding_{game_name}_{model_name}.txt"

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