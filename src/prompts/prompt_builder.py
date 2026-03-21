from __future__ import annotations
from typing import Any
from src.games.base_game import BaseGame

def build_rule_understanding_prompt(game_name: str, rules_text: str) -> str:
    """
    Build a structured prompt for rule understanding.
    The model extracts rule information into a fixed slot format.
    """
    if game_name == "tictactoe":
        required_fields = """board_size: ...
players: ...
symbols: ...
turn_order: ...
legal_move: ...
win_condition: ...
draw_condition: ...
start_player: ..."""
    elif game_name == "connect_four":
        required_fields = """board_size: ...
players: ...
turn_order: ...
move_type: ...
gravity: ...
illegal_full_column: ...
win_condition: ...
draw_condition: ...
start_player: ..."""
    else:
        required_fields = """rules_summary: ..."""

    return f"""You are given the rules of {game_name}.

Task:
Extract the essential rule information and write it in the exact format below.

Output requirements:
- Return ONLY the requested fields.
- Keep each field short and factual.
- Write exactly one line per field.
- If a detail is not explicitly stated, write: unknown
- Do NOT add bullet points or extra commentary.

Required output format:
{required_fields}

Rules:
{rules_text}
"""

def build_rule_error_detection_prompt(
    game_name: str,
    clean_rules: str,
    broken_rules: str,
) -> str:
    """Build a prompt for identifying inconsistencies in rules."""
    return f"""You are given two versions of the rules for {game_name}.

Task:
Identify inconsistencies, errors, or contradictions in the broken version compared to the clean version.

Output requirements:
- Return ONLY a bullet list of issues.
- Each bullet must be short and specific.

Clean rules:
{clean_rules}

Broken rules:
{broken_rules}
"""

def build_game_generation_prompt(seed_idea: str) -> str:
    """Build a prompt for inventing a new game."""
    return f"""Invent a simple board or turn-based game.

Output requirements:
- Return ONLY these 5 sections:
1. Game name
2. Objective
3. Setup
4. Rules
5. Example turn

Optional idea to inspire the game: {seed_idea}
"""

def build_move_prediction_prompt(
    game: BaseGame,
    rules_text: str,
    state: Any,
    include_legal_moves: bool = True,
) -> str:
    """
    CORE GAME OF THOUGHTS PROMPT:
    Forces the model to perform spatial analysis and strategy before moving.
    """
    state_text = game.state_to_text(state)
    current_player = state.current_player
    
    legal_moves_block = ""
    if include_legal_moves:
        try:
            legal_moves = game.get_legal_moves(state)
            legal_moves_text = ", ".join(game.move_to_text(m) for m in legal_moves)
            legal_moves_block = f"LEGAL MOVES AVAILABLE: {legal_moves_text}"
        except Exception:
            legal_moves_block = ""

    # Specific formatting instructions based on game type
    if game.name == "tictactoe":
        move_format = "FINAL MOVE FORMAT: (row, column). Example: (1, 2)"
    elif game.name == "connect_four":
        move_format = "FINAL MOVE FORMAT: Provide only the column index (0-6). Example: 3"
    else:
        move_format = "FINAL MOVE FORMAT: Provide the move value."

    return f"""You are playing {game.name} as Player {current_player}.

RULES:
{rules_text}

CURRENT BOARD STATE:
{state_text}

{legal_moves_block}

INSTRUCTIONS for 'Game of Thoughts' reasoning:
1. SPATIAL ANALYSIS: Describe the current board. Where are your pieces? Where are the opponent's? 
2. THREAT ASSESSMENT: Are there any immediate 3-in-a-row threats you need to block or 4-in-a-row opportunities to take?
3. STRATEGY: Explain the logic behind your next move.
4. FINAL MOVE: Conclude with your move in the required format.

{move_format}

IMPORTANT: You must show your reasoning steps 1-3 before providing the FINAL MOVE."""