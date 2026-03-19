from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MoveEvalResult:
    total_cases: int
    parse_successes: int
    valid_moves: int
    invalid_moves: int
    exact_matches: int = 0

    @property
    def parse_success_rate(self) -> float:
        return self.parse_successes / self.total_cases if self.total_cases else 0.0

    @property
    def valid_move_rate(self) -> float:
        return self.valid_moves / self.total_cases if self.total_cases else 0.0

    @property
    def invalid_move_rate(self) -> float:
        return self.invalid_moves / self.total_cases if self.total_cases else 0.0

    @property
    def exact_match_accuracy(self) -> float:
        return self.exact_matches / self.total_cases if self.total_cases else 0.0


def evaluate_single_move(game, state: Any, raw_response: str, expected_move: Any | None = None) -> dict:
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
    return MoveEvalResult(
        total_cases=len(rows),
        parse_successes=sum(1 for r in rows if r["parse_success"]),
        valid_moves=sum(1 for r in rows if r["is_valid"]),
        invalid_moves=sum(1 for r in rows if not r["is_valid"]),
        exact_matches=sum(1 for r in rows if r.get("exact_match", False)),
    )