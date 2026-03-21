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


SECTION_ALIASES = {
    "game name": ["game name", "name"],
    "objective": ["objective", "goal", "aim"],
    "setup": ["setup", "starting setup", "preparation"],
    "rules": ["rules", "how to play", "gameplay"],
    "example turn": ["example turn", "example", "sample turn"],
}


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
    """
    Check whether the generated game includes the required sections.
    """
    lower = text.lower()

    found = {}
    for section, aliases in SECTION_ALIASES.items():
        found[section] = any(alias in lower for alias in aliases)

    coverage = sum(found.values()) / len(REQUIRED_SECTIONS)
    return {"found": found, "coverage": coverage}


def heuristic_clarity_score(text: str) -> int:
    """
    Heuristic clarity score from 1 to 5.
    """
    lower = text.lower()
    score = 1

    if any(x in lower for x in ["objective", "goal"]):
        score += 1
    if any(x in lower for x in ["rules", "how to play"]):
        score += 1
    if any(x in lower for x in ["turn", "player", "win", "lose", "draw"]):
        score += 1
    if any(x in lower for x in ["example turn", "example", "setup"]):
        score += 1

    return min(score, 5)


def heuristic_consistency_score(text: str) -> int:
    """
    Heuristic consistency score from 1 to 5.
    """
    lower = text.lower()
    contradictions = 0

    if "two-player" in lower and "three players" in lower:
        contradictions += 1

    if "roll a die" in lower and "no randomness" in lower:
        contradictions += 1

    if ("win" not in lower and "winner" not in lower and
            "objective" not in lower and "goal" not in lower):
        contradictions += 1

    if "rules" in lower and "example turn" not in lower and "example" not in lower:
        contradictions += 1

    return max(1, 5 - contradictions)


def heuristic_balance_score(text: str) -> int:
    """
    Heuristic balance score from 1 to 5.
    """
    lower = text.lower()
    score = 2

    if any(x in lower for x in ["both players", "each player starts with", "same number"]):
        score += 2

    if any(x in lower for x in ["first player advantage", "goes first and wins immediately"]):
        score -= 1

    return max(1, min(score, 5))


def heuristic_fun_score(text: str) -> int:
    """
    Heuristic fun score from 1 to 5.
    """
    lower = text.lower()
    score = 2

    if any(x in lower for x in ["strategy", "risk", "treasure", "special ability", "interaction"]):
        score += 2

    if "example turn" in lower or "example" in lower:
        score += 1

    return max(1, min(score, 5))


def lightweight_playability_check(text: str, section_info: dict) -> bool:
    """
    Lightweight structural playability check.
    """
    lower = text.lower()

    has_players = "player" in lower
    has_objective = any(x in lower for x in ["objective", "goal", "win", "winner"])
    has_turn_logic = "turn" in lower
    has_setup = section_info["found"].get("setup", False)
    has_rules = section_info["found"].get("rules", False)
    full_structure = section_info["coverage"] == 1.0

    return all([
        full_structure,
        has_players,
        has_objective,
        has_turn_logic,
        has_setup,
        has_rules,
    ])


def evaluate_generated_game(text: str) -> dict:
    """
    Evaluate a generated game using lightweight heuristic metrics.
    """
    section_info = has_required_sections(text)
    playable = lightweight_playability_check(text, section_info)

    return {
        "section_coverage": section_info["coverage"],
        "sections_found": section_info["found"],
        "clarity": heuristic_clarity_score(text),
        "internal_consistency": heuristic_consistency_score(text),
        "balance": heuristic_balance_score(text),
        "fun_factor": heuristic_fun_score(text),
        "playable": playable,
    }