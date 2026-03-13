def get_rule_explanation_prompt(rules_text: str) -> str:
    return f"""
You are given the rules of a board game.

Game rules:
{rules_text}

Task:
1. Explain the rules clearly in bullet points.
2. Keep all important constraints.
3. Do not invent new rules.
"""


def get_rule_error_detection_prompt(rules_text: str) -> str:
    return f"""
You are given the rules of a board game.

Game rules:
{rules_text}

Task:
1. Identify missing or ambiguous rules.
2. Explain why they are problematic.
3. Suggest a corrected version of the rules.
"""


def get_valid_move_prompt(rules_text: str, board_text: str, player: str) -> str:
    return f"""
You are given the rules of Tic-Tac-Toe and the current board state.

Rules:
{rules_text}

Board state:
{board_text}

Current player: {player}

Task:
Suggest one valid move.

Return ONLY in this format:
row=<row>, col=<col>

Use zero-based indexing.
"""


def get_game_generation_prompt(theme: str) -> str:
    return f"""
Design a simple two-player board game.

Theme: {theme}

Provide:
1. Game name
2. Objective
3. Setup
4. Turn structure
5. Rules
6. Winning condition

Ensure the game rules are logically consistent.
"""