from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MoveEvalResult:
    """
    Aggregate results for single-move prediction evaluation.

    Attributes:
        total_cases: Number of evaluated move-prediction cases.
        parse_successes: Number of responses that could be parsed into a move.
        valid_moves: Number of parsed moves that were legal in the given state.
        invalid_moves: Number of responses that were either unparsable or illegal.
        exact_matches: Number of predictions matching the expected move exactly.
    """
    total_cases: int
    parse_successes: int
    valid_moves: int
    invalid_moves: int
    exact_matches: int = 0

    @property
    def parse_success_rate(self) -> float:
        """
        Fraction of responses that were successfully parsed.
        """
        return self.parse_successes / self.total_cases if self.total_cases else 0.0

    @property
    def valid_move_rate(self) -> float:
        """
        Fraction of cases where the predicted move was valid.
        """
        return self.valid_moves / self.total_cases if self.total_cases else 0.0

    @property
    def invalid_move_rate(self) -> float:
        """
        Fraction of cases where the predicted move was invalid or unparsable.
        """
        return self.invalid_moves / self.total_cases if self.total_cases else 0.0

    @property
    def exact_match_accuracy(self) -> float:
        """
        Fraction of cases where the predicted move exactly matched the expected move.
        """
        return self.exact_matches / self.total_cases if self.total_cases else 0.0


def evaluate_single_move(game, state: Any, raw_response: str, expected_move: Any | None = None) -> dict:
    """
    Evaluate one model response for a single move-prediction task.

    Args:
        game: Game object implementing parse_move, is_valid_move, and move_to_text.
        state: Current game state.
        raw_response: Raw model output.
        expected_move: Optional gold move for exact-match comparison.

    Returns:
        Dictionary containing parsing, validity, and exact-match information.
    """
    try:
        parsed_move = game.parse_move(raw_response)
        parse_success = True
    except Exception:
        parsed_move = None
        parse_success = False

    is_valid = parse_success and game.is_valid_move(state, parsed_move)
    exact_match = expected_move is not None and parse_success and parsed_move == expected_move

    return {
        "raw_response": raw_response,
        "parsed_move": game.move_to_text(parsed_move) if parse_success else None,
        "parse_success": parse_success,
        "is_valid": is_valid,
        "exact_match": exact_match,
    }


def aggregate_move_results(rows: list[dict]) -> MoveEvalResult:
    """
    Aggregate a list of single-move evaluation records.

    Args:
        rows: List of dictionaries returned by evaluate_single_move.

    Returns:
        MoveEvalResult with overall rates and counts.
    """
    return MoveEvalResult(
        total_cases=len(rows),
        parse_successes=sum(1 for r in rows if r["parse_success"]),
        valid_moves=sum(1 for r in rows if r["is_valid"]),
        invalid_moves=sum(1 for r in rows if not r["is_valid"]),
        exact_matches=sum(1 for r in rows if r.get("exact_match", False)),
    )