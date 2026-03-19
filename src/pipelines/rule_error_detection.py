from src.data.game_loader import load_game_data
from src.games.registry import get_game
from src.prompts.prompt_builder import build_rule_error_detection_prompt


def run_rule_error_detection(game_slug: str, model) -> dict:
    data = load_game_data(game_slug)

    if not data.get("broken_rules_text"):
        raise ValueError(f"No broken rules file found for game '{game_slug}'")

    game = get_game(game_slug)

    prompt = build_rule_error_detection_prompt(
        game_name=game.name,
        clean_rules=data["rules_text"],
        broken_rules=data["broken_rules_text"],
    )

    response = model.generate(prompt)

    return {
        "game_slug": game_slug,
        "game_name": game.name,
        "prompt": prompt,
        "clean_rules_text": data["rules_text"],
        "broken_rules_text": data["broken_rules_text"],
        "response": response,
    }