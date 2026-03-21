import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3] 

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
from src.config import SUPPORTED_MODELS
from src.prompts.prompt_builder import build_rule_error_detection_prompt
from src.llm.model_loader import load_model


def safe_filename(text: str) -> str:
    return text.replace("/", "_").replace("\\", "_").replace(":", "_")


def clean_response(text: str) -> str:
    """
    Clean model output before saving.
    """
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>")[-1].strip()

    return text


def parse_args():
    if "--model" not in sys.argv or "--game" not in sys.argv:
        raise ValueError(
            f"Usage: python experiments/rule_error_detection.py "
            f"--model <{'|'.join(SUPPORTED_MODELS)}> --game <tictactoe|connect_four>"
        )

    model_name = sys.argv[sys.argv.index("--model") + 1].lower()
    game_name = sys.argv[sys.argv.index("--game") + 1].lower()
    return model_name, game_name


def load_clean_rules(game_name: str) -> str:
    path = ROOT / "data" / "raw" / game_name / "rules.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_cases(game_name: str) -> list[dict]:
    if game_name == "tictactoe":
        path = ROOT / "data" / "processed" / "tictactoe" / "rule_error_cases_tictactoe.json"
    elif game_name == "connect_four":
        path = ROOT / "data" / "processed" / "connect_four" / "rule_error_cases_connect_four.json"
    else:
        raise ValueError(f"Unsupported game: {game_name}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    model_name, game_name = parse_args()
    safe_model_name = safe_filename(model_name)

    model = load_model(model_name)
    clean_rules = load_clean_rules(game_name)
    cases = load_cases(game_name)

    prompts_dir = ROOT / "results" / "prompts" / "rule_error_detection"
    responses_dir = ROOT / "results" / "responses" / "rule_error_detection"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    for case in cases:
        broken_rules = case["rules_text"]

        prompt = build_rule_error_detection_prompt(
            game_name=game_name,
            clean_rules=clean_rules,
            broken_rules=broken_rules,
        )

        raw_response = model.generate(prompt)
        response = clean_response(raw_response)

        prompt_path = prompts_dir / (
            f"rule_error_detection_{game_name}_{safe_model_name}_{case['id']}_prompt.txt"
        )
        response_path = responses_dir / (
            f"rule_error_detection_{game_name}_{safe_model_name}_{case['id']}.txt"
        )

        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        with open(response_path, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"Saved prompt to: {prompt_path}")
        print(f"Saved response to: {response_path}")


if __name__ == "__main__":
    main()