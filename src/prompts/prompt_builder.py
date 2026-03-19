from __future__ import annotations

from typing import Any

from src.games.base_game import BaseGame


def build_rule_understanding_prompt(game_name: str, rules_text: str) -> str:
    return f"""You are given the rules of {game_name}.

Task:
Rewrite the rules as briefly as possible while preserving all essential information.

Output requirements:
- Return ONLY the rewritten rules.
- Use short bullet points.
- Do NOT add any introduction.
- Do NOT add any conclusion.
- Do NOT add explanations beyond the rules.
- Keep the wording concise and factual.
- Do NOT output <think> tags.
- Do NOT output reasoning.

Rules:
{rules_text}
"""


def build_rule_error_detection_prompt(
    game_name: str,
    clean_rules: str,
    broken_rules: str,
) -> str:
    return f"""You are given two versions of the rules for {game_name}.

Task:
Identify inconsistencies, errors, or contradictions in the broken version.

Output requirements:
- Return ONLY a bullet list of issues.
- Each bullet must be short and specific.
- Do NOT add any introduction.
- Do NOT add any conclusion.
- Do NOT output <think> tags.
- Do NOT output reasoning.

Clean rules:
{clean_rules}

Broken rules:
{broken_rules}
"""


def build_game_generation_prompt(seed_idea: str) -> str:
    return f"""Invent a simple board or turn-based game.

Output requirements:
- Return ONLY these 5 sections in this exact order:
1. Game name
2. Objective
3. Setup
4. Rules
5. Example turn
- Keep each section concise.
- Do NOT add extra commentary.
- Do NOT add analysis or design justification.
- Do NOT output <think> tags.
- Do NOT output reasoning.

Optional idea to inspire the game: {seed_idea}
"""


def build_move_prediction_prompt(
    game: BaseGame,
    rules_text: str,
    state: Any,
    include_legal_moves: bool = True,
) -> str:
    state_text = game.state_to_text(state)

    legal_moves_block = ""
    if include_legal_moves:
        try:
            legal_moves = game.get_legal_moves(state)
            legal_moves_text = ", ".join(game.move_to_text(m) for m in legal_moves)
            legal_moves_block = f"\nLegal moves: {legal_moves_text}\n"
        except Exception:
            legal_moves_block = ""

    if game.name == "tictactoe":
        output_instruction = """IMPORTANT:
Return ONLY the move in this exact format:
(row, column)

Valid examples:
(0, 0)
(1, 2)

Invalid examples:
The move is (0, 0)
Move: (1, 2)
I choose (2, 2)

Return exactly one move.
Do NOT include explanation.
Do NOT include any extra text.
Do NOT output <think> tags.
Do NOT output reasoning.
"""
    elif game.name == "connect_four":
        output_instruction = """IMPORTANT:
Return ONLY the column index as a single integer.

Valid examples:
0
3
6

Invalid examples:
Column 3
Move: 4
I choose 2

Return exactly one move.
Do NOT include explanation.
Do NOT include any extra text.
Do NOT output <think> tags.
Do NOT output reasoning.
"""
    else:
        output_instruction = """IMPORTANT:
Return ONLY the move.
Do NOT include explanation or extra text.
Do NOT output <think> tags.
Do NOT output reasoning.
"""

    return f"""You are playing {game.name}.

Rules:
{rules_text}

Current game state:
{state_text}
{legal_moves_block}
Choose the best next move for the current player.

{output_instruction}"""