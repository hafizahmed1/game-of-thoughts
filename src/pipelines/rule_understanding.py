from src.data.game_loader import load_game_data
from src.games.registry import get_game
from src.prompts.prompt_builder import build_rule_understanding_prompt


def clean_response(text: str) -> str:
    """
    Clean model output before returning it from the pipeline.

    This keeps rule-understanding evaluation more stable by removing
    unexpected reasoning tags and extra whitespace.
    """
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>")[-1].strip()

    return text


def run_rule_understanding(game_slug: str, model) -> dict:
    data = load_game_data(game_slug)
    game = get_game(game_slug)

    prompt = build_rule_understanding_prompt(
        game_name=game.name,
        rules_text=data["rules_text"],
    )

    raw_response = model.generate(prompt)
    response = clean_response(raw_response)

    return {
        "game_slug": game_slug,
        "game_name": game.name,
        "prompt": prompt,
        "response": response,
    }