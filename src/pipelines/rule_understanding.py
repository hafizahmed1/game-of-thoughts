from src.data.game_loader import load_game_data
from src.games.registry import create_game
from src.prompts.prompt_builder import build_rule_understanding_prompt


def run_rule_understanding(game_slug: str, model) -> dict:
    data = load_game_data(game_slug)
    game = create_game(game_slug, data["rules_text"])

    prompt = build_rule_understanding_prompt(
        game_name=game.name,
        rules_text=game.get_rules_text(),
    )

    response = model.generate(prompt)

    return {
        "game_slug": game_slug,
        "game_name": game.name,
        "prompt": prompt,
        "response": response,
    }