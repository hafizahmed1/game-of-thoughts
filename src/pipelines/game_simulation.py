from __future__ import annotations

from dataclasses import asdict, dataclass
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


def run_game_simulation(
    *,
    game: BaseGame,
    rules_text: str,
    initial_state: Any,
    model,
    max_turns: int = 10,
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
            raw_response = model.generate(prompt)
        except Exception:
            raw_response = "INVALID_RESPONSE"

        raw_response = raw_response.strip() if isinstance(raw_response, str) else "INVALID_RESPONSE"
        raw_response = raw_response.splitlines()[0].strip() if raw_response else "INVALID_RESPONSE"

        parsed_move = None
        parsed_move_text = None
        move_valid = False

        try:
            parsed_move = game.parse_move(raw_response)
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
                    raw_response=raw_response,
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
                raw_response=raw_response,
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