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
    if not text:
        return ""

    # Closed think block: keep what comes after it
    if "</think>" in text.lower():
        parts = re.split(r"</think>", text, flags=re.IGNORECASE)
        tail = parts[-1].strip()
        if tail:
            return tail
        return ""

    # Unclosed think block: try to remove the opening tag and keep any tail after the last blank line
    if "<think>" in text.lower():
        text = re.sub(r"<think>\s*", "", text, flags=re.IGNORECASE).strip()

        # If model never gives a final answer outside thinking, treat as invalid
        return ""

    return text

def normalize_model_output(game: BaseGame, raw_response: str) -> str:
    text = extract_final_answer_region(raw_response)

    if not text:
        return "INVALID_RESPONSE"

    # Prefer the last non-empty line as the final answer
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        candidate_text = lines[-1]
    else:
        candidate_text = text

    if game.name == "tictactoe":
        # exact tuple, choose the LAST one found
        matches = re.findall(r"\(\s*([0-2])\s*,\s*([0-2])\s*\)", candidate_text)
        if matches:
            r, c = matches[-1]
            return f"({r}, {c})"

        matches = re.findall(
            r"\brow\s*=?\s*([0-2])\D+col(?:umn)?\s*=?\s*([0-2])\b",
            candidate_text,
            flags=re.IGNORECASE,
        )
        if matches:
            r, c = matches[-1]
            return f"({r}, {c})"

        matches = re.findall(r"\b([0-2])\s*,\s*([0-2])\b", candidate_text)
        if matches:
            r, c = matches[-1]
            return f"({r}, {c})"

        matches = re.findall(r"\b([0-2])\s+([0-2])\b", candidate_text)
        if matches:
            r, c = matches[-1]
            return f"({r}, {c})"

        return "INVALID_RESPONSE"

    if game.name == "connect_four":
        # Prefer the last single-column answer
        matches = re.findall(r"\bcolumn\s*=?\s*([0-6])\b", candidate_text, flags=re.IGNORECASE)
        if matches:
            return matches[-1]

        matches = re.findall(r"\b([0-6])\b", candidate_text)
        if matches:
            return matches[-1]

        return "INVALID_RESPONSE"

    return candidate_text if candidate_text else "INVALID_RESPONSE"


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
                game_name=game.name,
                completed_turns=turn_index,
                stopped_reason="terminal_state_reached",
                winner=game.get_winner(state),
                final_state_text=game.state_to_text(state),
                turns=turns,
            )

        player = state.current_player
        state_text_before = game.state_to_text(state)

        prompt = build_move_prediction_prompt(
            game=game,
            rules_text=rules_text,
            state=state,
            include_legal_moves=include_legal_moves,
        )

        try:
            full_raw_response = model.generate(prompt)
        except Exception as e:
            full_raw_response = f"ERROR: {type(e).__name__}: {e}"

        if not isinstance(full_raw_response, str):
            full_raw_response = "INVALID_RESPONSE"

        normalized_response = normalize_model_output(game, full_raw_response)

        parsed_move = None
        parsed_move_text = None
        move_valid = False

        try:
            parsed_move = game.parse_move(normalized_response)
            parsed_move_text = game.move_to_text(parsed_move)
            move_valid = game.is_valid_move(state, parsed_move)
        except Exception:
            move_valid = False

        if not move_valid:
            turns.append(
                TurnRecord(
                    turn_index=turn_index,
                    player=player,
                    state_text_before=state_text_before,
                    raw_response=full_raw_response,
                    parsed_move_text=parsed_move_text,
                    move_valid=False,
                    winner_after_move=game.get_winner(state),
                    terminal_after_move=game.is_terminal(state),
                )
            )

            return GameSimulationResult(
                game_name=game.name,
                completed_turns=turn_index,
                stopped_reason="invalid_or_unparseable_move",
                winner=game.get_winner(state),
                final_state_text=game.state_to_text(state),
                turns=turns,
            )

        state = game.apply_move(state, parsed_move)

        turns.append(
            TurnRecord(
                turn_index=turn_index,
                player=player,
                state_text_before=state_text_before,
                raw_response=full_raw_response,
                parsed_move_text=parsed_move_text,
                move_valid=True,
                winner_after_move=game.get_winner(state),
                terminal_after_move=game.is_terminal(state),
            )
        )

        if game.is_terminal(state):
            return GameSimulationResult(
                game_name=game.name,
                completed_turns=turn_index + 1,
                stopped_reason="terminal_state_reached",
                winner=game.get_winner(state),
                final_state_text=game.state_to_text(state),
                turns=turns,
            )

    return GameSimulationResult(
        game_name=game.name,
        completed_turns=max_turns,
        stopped_reason="max_turns_reached",
        winner=game.get_winner(state),
        final_state_text=game.state_to_text(state),
        turns=turns,
    )