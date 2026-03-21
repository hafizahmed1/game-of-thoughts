from src.data.game_loader import load_game_data
from src.prompts.prompt_builder import build_rule_error_detection_prompt


def clean_response(text: str) -> str:
    """
    Clean model output before returning it from the pipeline.
    """
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>")[-1].strip()

    return text


def run_rule_error_detection(game_slug: str, model, broken_rules_text: str) -> dict:
    """
    Run rule error detection for one broken-rule case.

    Args:
        game_slug: Game name, e.g. tictactoe or connect_four.
        model: Loaded model object.
        broken_rules_text: Corrupted rule text to evaluate.

    Returns:
        Dictionary containing prompt and response.
    """
    data = load_game_data(game_slug)

    prompt = build_rule_error_detection_prompt(
        game_name=game_slug,
        clean_rules=data["rules_text"],
        broken_rules=broken_rules_text,
    )

    raw_response = model.generate(prompt)
    response = clean_response(raw_response)

    return {
        "game_slug": game_slug,
        "prompt": prompt,
        "response": response,
    }