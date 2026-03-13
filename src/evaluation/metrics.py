import re


def parse_move(text: str):
    pattern = r"row\s*=\s*(\d+)\s*,\s*col\s*=\s*(\d+)"
    match = re.search(pattern, text)

    if not match:
        return None

    row = int(match.group(1))
    col = int(match.group(2))
    return row, col


def move_format_correct(text: str):
    return parse_move(text) is not None


def rule_completeness_score(model_output: str, required_keywords: list[str]) -> float:
    output_lower = model_output.lower()
    found = sum(1 for keyword in required_keywords if keyword.lower() in output_lower)
    return found / len(required_keywords) if required_keywords else 0.0