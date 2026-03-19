from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class RuleUnderstandingScore:
    covered_items: int
    total_items: int
    hallucinated_items: int

    @property
    def completeness(self) -> float:
        return self.covered_items / self.total_items if self.total_items else 0.0


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def text_contains_any(text: str, candidates: list[str]) -> bool:
    text = normalize_text(text)
    return any(normalize_text(c) in text for c in candidates)


def score_rule_summary(model_output: str, gold_schema: dict[str, Any]) -> dict[str, Any]:
    required_items = gold_schema["required_items"]

    covered = 0
    missing = []

    for slot, aliases in required_items.items():
        if text_contains_any(model_output, aliases):
            covered += 1
        else:
            missing.append(slot)

    forbidden = gold_schema.get("forbidden_items", {})
    hallucinated = []

    for slot, aliases in forbidden.items():
        if text_contains_any(model_output, aliases):
            hallucinated.append(slot)

    score = RuleUnderstandingScore(
        covered_items=covered,
        total_items=len(required_items),
        hallucinated_items=len(hallucinated),
    )

    return {
        "completeness": score.completeness,
        "covered_items": covered,
        "total_items": len(required_items),
        "missing_items": missing,
        "hallucinated_items": hallucinated,
    }


def parse_error_candidates(text: str) -> list[str]:
    text = text.strip()
    if normalize_text(text) == "no_errors":
        return []

    candidates: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("-") or stripped.startswith("*"):
            candidates.append(normalize_text(stripped[1:]))
            continue

        if re.match(r"^\d+[\.\)]\s+", stripped):
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", stripped)
            candidates.append(normalize_text(cleaned))
            continue

        if len(stripped.split()) >= 4:
            candidates.append(normalize_text(stripped))

    seen = set()
    deduped = []
    for c in candidates:
        if c not in seen:
            deduped.append(c)
            seen.add(c)

    return deduped


def token_overlap_match(a: str, b: str) -> bool:
    a_tokens = set(normalize_text(a).split())
    b_tokens = set(normalize_text(b).split())

    if not a_tokens or not b_tokens:
        return False

    overlap = len(a_tokens & b_tokens)
    return overlap >= 2


def score_error_detection(predicted_text: str, gold_error_labels: list[str]) -> dict[str, Any]:
    predicted_candidates = parse_error_candidates(predicted_text)
    gold = [normalize_text(label) for label in gold_error_labels]

    if len(gold) == 0:
        tp = 0
        fp = len(predicted_candidates)
        fn = 0
        precision = 0.0 if fp > 0 else 1.0
        recall = 1.0
        f1 = 0.0 if fp > 0 else 1.0
        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "predicted_candidates": predicted_candidates,
            "matched_gold_indices": [],
        }

    matched_gold: set[int] = set()
    matched_pred: set[int] = set()

    for i, g in enumerate(gold):
        for j, p in enumerate(predicted_candidates):
            if g in p or p in g or token_overlap_match(g, p):
                matched_gold.add(i)
                matched_pred.add(j)

    tp = len(matched_gold)
    fp = max(0, len(predicted_candidates) - len(matched_pred))
    fn = max(0, len(gold) - len(matched_gold))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predicted_candidates": predicted_candidates,
        "matched_gold_indices": sorted(matched_gold),
    }