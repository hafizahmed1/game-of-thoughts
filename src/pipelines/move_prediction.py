from src.data.game_loader import load_game_data
from src.games.registry import create_game
from src.prompts.prompt_builder import (
    build_valid_move_prompt_baseline,
    build_valid_move_prompt_constrained,
)


def predict_one_move(game_slug: str, model, state, prompt_variant: str = "baseline") -> dict:
    data = load_game_data(game_slug)
    game = create_game(game_slug, data["rules_text"])

    legal_moves = game.get_legal_moves(state, state.current_player)

    if prompt_variant == "baseline":
        prompt = build_valid_move_prompt_baseline(
            game_name=game.name,
            rules_text=game.get_rules_summary(),
            state_text=game.state_to_text(state),
            player=state.current_player,
        )
    elif prompt_variant == "constrained":
        prompt = build_valid_move_prompt_constrained(
            game_name=game.name,
            rules_text=game.get_rules_summary(),
            state_text=game.state_to_text(state),
            player=state.current_player,
            legal_moves=legal_moves,
        )
    else:
        raise ValueError(f"Unsupported prompt variant: {prompt_variant}")

    raw_response = model.generate(prompt)

    try:
        move = game.parse_move(raw_response)
        is_valid = game.is_valid_move(state, move, state.current_player)
    except Exception:
        move = None
        is_valid = False

    return {
        "game_slug": game_slug,
        "game_name": game.name,
        "prompt_variant": prompt_variant,
        "state": game.state_to_text(state),
        "player": state.current_player,
        "prompt": prompt,
        "legal_moves": legal_moves,
        "raw_response": raw_response,
        "parsed_move": move,
        "is_valid": is_valid,
    }


def simulate_multiple_turns(
    game_slug: str,
    model,
    max_turns: int = 9,
    prompt_variant: str = "baseline",
) -> dict:
    data = load_game_data(game_slug)
    game = create_game(game_slug, data["rules_text"])

    state = game.initial_state()
    history = []

    for turn_idx in range(max_turns):
        if game.is_terminal(state):
            break

        current_player = state.current_player
        result = predict_one_move(
            game_slug=game_slug,
            model=model,
            state=state,
            prompt_variant=prompt_variant,
        )

        history.append({
            "turn": turn_idx + 1,
            "player": current_player,
            "state_before": result["state"],
            "legal_moves": result["legal_moves"],
            "raw_response": result["raw_response"],
            "parsed_move": result["parsed_move"],
            "is_valid": result["is_valid"],
        })

        if not result["is_valid"]:
            break

        state = game.apply_move(state, result["parsed_move"], current_player)

    attempted_turns = len(history)
    valid_turns = sum(1 for step in history if step["is_valid"])
    valid_turn_rate = valid_turns / attempted_turns if attempted_turns > 0 else 0.0

    return {
        "game_slug": game_slug,
        "game_name": game.name,
        "prompt_variant": prompt_variant,
        "final_state": game.state_to_text(state),
        "winner": game.get_winner(state),
        "terminal": game.is_terminal(state),
        "attempted_turns": attempted_turns,
        "valid_turns": valid_turns,
        "valid_turn_rate": valid_turn_rate,
        "history": history,
    }