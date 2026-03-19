from __future__ import annotations

import re
from dataclasses import dataclass


REQUIRED_SECTIONS = [
    "game name",
    "objective",
    "setup",
    "rules",
    "example turn",
]


@dataclass
class GenerationScore:
    section_coverage: float
    clarity: int
    consistency: int
    balance: int
    fun_factor: int
    playable: bool


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def has_required_sections(text: str) -> dict:
    lower = text.lower()
    found = {section: (section in lower) for section in REQUIRED_SECTIONS}
    coverage = sum(found.values()) / len(REQUIRED_SECTIONS)
    return {"found": found, "coverage": coverage}


def heuristic_clarity_score(text: str) -> int:
    score = 1
    lower = text.lower()
    if "objective" in lower and "rules" in lower:
        score += 1
    if len(text.split()) > 80:
        score += 1
    if any(x in lower for x in ["turn", "player", "win", "lose", "draw"]):
        score += 1
    if any(x in lower for x in ["example", "setup"]):
        score += 1
    return min(score, 5)


def heuristic_consistency_score(text: str) -> int:
    lower = text.lower()
    contradictions = 0
    if "two-player" in lower and "three players" in lower:
        contradictions += 1
    if "roll a die" in lower and "no randomness" in lower:
        contradictions += 1
    if "winner" not in lower and "objective" not in lower:
        contradictions += 1

    return max(1, 5 - contradictions)


def heuristic_balance_score(text: str) -> int:
    lower = text.lower()
    score = 2
    if any(x in lower for x in ["both players", "each player starts with", "same number"]):
        score += 2
    if any(x in lower for x in ["first player advantage", "goes first and wins immediately"]):
        score -= 1
    return max(1, min(score, 5))


def heuristic_fun_score(text: str) -> int:
    lower = text.lower()
    score = 2
    if any(x in lower for x in ["strategy", "risk", "treasure", "special ability", "interaction"]):
        score += 2
    if "example turn" in lower:
        score += 1
    return max(1, min(score, 5))


def evaluate_generated_game(text: str, playable: bool = False) -> dict:
    section_info = has_required_sections(text)

    return {
        "section_coverage": section_info["coverage"],
        "sections_found": section_info["found"],
        "clarity": heuristic_clarity_score(text),
        "internal_consistency": heuristic_consistency_score(text),
        "balance": heuristic_balance_score(text),
        "fun_factor": heuristic_fun_score(text),
        "playable": playable,
    }