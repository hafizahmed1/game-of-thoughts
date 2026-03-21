from __future__ import annotations

import re
import ast
from dataclasses import dataclass
from typing import Any

@dataclass
class RuleUnderstandingScore:
    correct_items: int
    filled_items: int
    total_items: int
    hallucinated_items: int

    @property
    def completeness(self) -> float:
        return self.correct_items / self.total_items if self.total_items else 0.0

    @property
    def precision(self) -> float:
        return self.correct_items / self.filled_items if self.filled_items else 0.0

    @property
    def f1(self) -> float:
        if self.precision + self.completeness == 0:
            return 0.0
        return 2 * self.precision * self.completeness / (self.precision + self.completeness)


def normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace."""
    if not text:
        return ""
    # Remove punctuation for better matching
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text.strip().lower())


def flexible_match(text: str, candidate: str) -> bool:
    """
    Improved matching: 
    1. Check substring containment first.
    2. Fallback to token overlap with a lenient threshold for short phrases.
    """
    text_norm = normalize_text(text)
    cand_norm = normalize_text(candidate)

    # Direct substring match (e.g., "7x6" inside "board is 7x6")
    if cand_norm in text_norm or text_norm in cand_norm:
        return True

    text_tokens = set(text_norm.split())
    cand_tokens = set(cand_norm.split())

    if not text_tokens or not cand_tokens:
        return False

    overlap = len(text_tokens & cand_tokens)
    
    # If candidate is short (1-2 words), 1 token match is usually sufficient
    if len(cand_tokens) <= 2:
        return overlap >= 1
    
    # Otherwise, require at least 50% of the candidate's tokens
    return overlap >= (len(cand_tokens) // 2)


def text_contains_any(text: str, candidates: list[str]) -> bool:
    """Check if model text matches any valid candidate using flexible logic."""
    for candidate in candidates:
        if flexible_match(text, candidate):
            return True
    return False


def parse_structured_rule_output(model_output: str, gold_schema: dict[str, Any]) -> dict[str, str]:
    """
    Extracts slots from output lines like 'board_size: 7x6'.
    Uses fuzzy slot matching to handle variations in keys.
    """
    required_items = gold_schema.get("required_items", {})
    parsed = {slot: "" for slot in required_items.keys()}

    for line in model_output.splitlines():
        if ":" not in line:
            continue

        key_part, value = line.split(":", 1)
        norm_key = normalize_text(key_part).replace(" ", "_")
        
        # Fuzzy match the Key to the Schema Slot
        for slot in parsed.keys():
            # Match if key is 'winning_condition' and slot is 'win_condition'
            if slot in norm_key or norm_key in slot:
                parsed[slot] = value.strip()
                break

    return parsed


def infer_slot_coverage_from_free_text(model_output: str, gold_schema: dict[str, Any]) -> dict[str, str]:
    """Fallback for unstructured text by scanning for schema aliases."""
    required_items = gold_schema.get("required_items", {})
    parsed = {slot: "" for slot in required_items.keys()}
    
    for slot, aliases in required_items.items():
        if text_contains_any(model_output, aliases):
            # Use the first alias as the 'found' value
            parsed[slot] = aliases[0]

    return parsed


def parse_rule_understanding_output(model_output: str, gold_schema: dict[str, Any]) -> dict[str, str]:
    """Try structured parsing first, then fallback to keyword inference."""
    parsed = parse_structured_rule_output(model_output, gold_schema)
    # If no keys were found at all, try scanning the whole text
    if all(not value for value in parsed.values()):
        return infer_slot_coverage_from_free_text(model_output, gold_schema)
    return parsed


def score_rule_summary(model_output: str, gold_schema: dict[str, Any]) -> dict[str, Any]:
    """Main entry point for Rule Understanding evaluation."""
    required_items = gold_schema.get("required_items", {})
    forbidden_items = gold_schema.get("forbidden_items", {})

    parsed_slots = parse_rule_understanding_output(model_output, gold_schema)

    correct_items_list = []
    incorrect_items_list = []
    missing_items_list = []
    filled_count = 0

    for slot, expected_aliases in required_items.items():
        value = parsed_slots.get(slot, "").strip()
        
        if not value or value.lower() == "unknown":
            missing_items_list.append(slot)
            continue

        filled_count += 1
        if text_contains_any(value, expected_aliases):
            correct_items_list.append(slot)
        else:
            incorrect_items_list.append(slot)

    # Hallucination check
    hallucinated_slots = []
    for slot, forbidden_aliases in forbidden_items.items():
        if text_contains_any(model_output, forbidden_aliases):
            hallucinated_slots.append(slot)

    score = RuleUnderstandingScore(
        correct_items=len(correct_items_list),
        filled_items=filled_count,
        total_items=len(required_items),
        hallucinated_items=len(hallucinated_slots),
    )

    return {
        "completeness": score.completeness,
        "precision": score.precision,
        "f1": score.f1,
        "correct_items": len(correct_items_list),
        "filled_items": filled_count,
        "total_items": len(required_items),
        "missing_items": missing_items_list,
        "incorrect_items": incorrect_items_list,
        "hallucinated_items": hallucinated_slots,
        "parsed_slots": parsed_slots,
    }


# --- RULE ERROR DETECTION SCORING ---

def parse_error_candidates(text: str) -> list[str]:
    """Parses a list of detected errors from model text."""
    if normalize_text(text) == "no errors" or not text.strip():
        return []

    candidates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped: continue
        # Remove list markers
        cleaned = re.sub(r"^[*\-\d\.\)]+\s*", "", stripped)
        if len(cleaned.split()) >= 2: # Ignore single-word noise
            candidates.append(normalize_text(cleaned))

    return list(dict.fromkeys(candidates)) # Dedup


def score_error_detection(predicted_text: str, gold_error_labels: list[str]) -> dict[str, Any]:
    """Calculates TP, FP, FN for rule error detection."""
    predicted_candidates = parse_error_candidates(predicted_text)
    gold = [normalize_text(label) for label in gold_error_labels]

    if not gold:
        fp = len(predicted_candidates)
        return {
            "tp": 0, "fp": fp, "fn": 0,
            "precision": 0.0 if fp > 0 else 1.0,
            "recall": 1.0, "f1": 0.0 if fp > 0 else 1.0,
            "predicted_candidates": predicted_candidates
        }

    matched_gold = set()
    matched_pred = set()

    for i, g in enumerate(gold):
        for j, p in enumerate(predicted_candidates):
            # Token overlap check for error detection
            g_tokens, p_tokens = set(g.split()), set(p.split())
            overlap = len(g_tokens & p_tokens)
            if g in p or p in g or overlap >= 2:
                matched_gold.add(i)
                matched_pred.add(j)

    tp = len(matched_gold)
    fp = max(0, len(predicted_candidates) - len(matched_pred))
    fn = max(0, len(gold) - len(matched_gold))

    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": prec, "recall": rec, "f1": f1,
        "predicted_candidates": predicted_candidates
    }