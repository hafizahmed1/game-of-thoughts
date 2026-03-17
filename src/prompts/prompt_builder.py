from __future__ import annotations

from src.games.base_game import BaseGame


def build_move_prediction_prompt(
    game: BaseGame,
    rules_text: str,
    state,
    include_legal_moves: bool = True,
) -> str:
    state_text = game.state_to_text(state)

    sections = [
        f"You are playing {game.name}.",
        "Read the rules and choose exactly one valid next move.",
        "",
        "Rules:",
        rules_text.strip(),
        "",
        "Current game state:",
        state_text,
        "",
    ]

    if include_legal_moves:
        legal_moves = list(game.get_legal_moves(state))
        legal_moves_text = ", ".join(game.move_to_text(move) for move in legal_moves)
        sections.extend(
            [
                "Legal moves:",
                legal_moves_text if legal_moves_text else "(none)",
                "",
            ]
        )

    sections.extend(
        [
            "Instructions:",
            game.get_move_format_instructions(),
            "Do not explain your answer.",
            "Do not output anything except the move.",
        ]
    )

    return "\n".join(sections)


def build_rule_understanding_prompt(game_name: str, rules_text: str) -> str:
    return (
        f"You are given the rules of {game_name}.\n\n"
        "Explain the rules clearly and concisely.\n\n"
        "Rules:\n"
        f"{rules_text.strip()}"
    )


def build_rule_error_detection_prompt(game_name: str, clean_rules: str, broken_rules: str) -> str:
    return (
        f"You are given two versions of the rules for {game_name}.\n"
        "Identify inconsistencies, errors, or contradictions in the broken version.\n\n"
        "Clean rules:\n"
        f"{clean_rules.strip()}\n\n"
        "Broken rules:\n"
        f"{broken_rules.strip()}"
    )


def build_game_generation_prompt(seed_idea: str | None = None) -> str:
    base = (
        "Invent a simple board or turn-based game.\n"
        "Provide:\n"
        "1. Game name\n"
        "2. Objective\n"
        "3. Setup\n"
        "4. Rules\n"
        "5. Example turn\n"
    )
    if seed_idea:
        base += f"\nOptional idea to inspire the game: {seed_idea.strip()}\n"
    return base