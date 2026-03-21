from __future__ import annotations
from dataclasses import asdict, dataclass
import re
from typing import Any
from src.games.base_game import BaseGame
from src.prompts.prompt_builder import build_move_prediction_prompt

@dataclass
class TurnRecord:
    turn_index: int
    player: str
    state_text_before: str
    raw_response: str
    parsed_move_text: str | None
    move_valid: bool
    winner_after_move: str | None
    terminal_after_move: bool

@dataclass
class GameSimulationResult:
    game_name: str
    completed_turns: int
    stopped_reason: str
    winner: str | None
    final_state_text: str
    turns: list[TurnRecord]

    def to_dict(self) -> dict:
        return {
            "game_name": self.game_name,
            "completed_turns": self.completed_turns,
            "stopped_reason": self.stopped_reason,
            "winner": self.winner,
            "final_state_text": self.final_state_text,
            "turns": [asdict(turn) for turn in self.turns],
        }

def extract_final_answer_region(raw_response: str) -> str:
    text = (raw_response or "").strip()
    if not text: return ""

    # Logic for models using <think> tags (like DeepSeek)
    if "</think>" in text.lower():
        parts = re.split(r"</think>", text, flags=re.IGNORECASE)
        text = parts[-1].strip()
    
    # Logic for our 'Game of Thoughts' format (looking for MOVE: or FINAL MOVE:)
    if "MOVE:" in text:
        parts = re.split(r"MOVE:", text, flags=re.IGNORECASE)
        text = parts[-1].strip()

    return text

def normalize_model_output(game: BaseGame, raw_response: str) -> str:
    text = extract_final_answer_region(raw_response)
    if not text: return "INVALID_RESPONSE"

    # Search specifically for coordinates or indices in the extracted final region
    if game.name == "tictactoe":
        matches = re.findall(r"\(\s*([0-2])\s*,\s*([0-2])\s*\)", text)
        if matches:
            r, c = matches[-1]
            return f"({r}, {c})"
    
    if game.name == "connect_four":
        matches = re.findall(r"\b([0-6])\b", text)
        if matches: return matches[-1]

    return "INVALID_RESPONSE"

def run_game_simulation(
    *,
    game: BaseGame,
    rules_text: str,
    initial_state: Any,
    model,
    max_turns: int = 1,
    include_legal_moves: bool = True,
) -> GameSimulationResult:
    state = initial_state
    turns: list[TurnRecord] = []

    for turn_index in range(max_turns):
        if game.is_terminal(state):
            return GameSimulationResult(
                game.name, turn_index, "terminal_state_reached", 
                game.get_winner(state), game.state_to_text(state), turns
            )

        player = state.current_player
        state_text_before = game.state_to_text(state)
        
        # Use the GoT prompt builder
        prompt = build_move_prediction_prompt(
            game=game, rules_text=rules_text, state=state, include_legal_moves=include_legal_moves
        )

        try:
            full_raw_response = model.generate(prompt)
        except Exception as e:
            full_raw_response = f"ERROR: {e}"

        normalized_response = normalize_model_output(game, full_raw_response)
        
        parsed_move = None
        parsed_move_text = None
        move_valid = False

        try:
            parsed_move = game.parse_move(normalized_response)
            parsed_move_text = game.move_to_text(parsed_move)
            move_valid = game.is_valid_move(state, parsed_move)
        except:
            move_valid = False

        # Apply move if valid
        if move_valid:
            state = game.apply_move(state, parsed_move)
            winner = game.get_winner(state)
            is_term = game.is_terminal(state)
        else:
            winner = game.get_winner(state)
            is_term = True # Stop on invalid move

        turns.append(TurnRecord(
            turn_index=turn_index,
            player=player,
            state_text_before=state_text_before,
            raw_response=full_raw_response,
            parsed_move_text=parsed_move_text,
            move_valid=move_valid,
            winner_after_move=winner,
            terminal_after_move=is_term
        ))

        if not move_valid:
            return GameSimulationResult(game.name, turn_index, "invalid_move", winner, state_text_before, turns)
        
        if is_term:
            return GameSimulationResult(game.name, turn_index + 1, "terminal_state_reached", winner, game.state_to_text(state), turns)

    return GameSimulationResult(game.name, max_turns, "max_turns_reached", game.get_winner(state), game.state_to_text(state), turns)