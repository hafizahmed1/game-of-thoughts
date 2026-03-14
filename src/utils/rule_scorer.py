def score_tictactoe_rules(response: str):
    """
    Simple heuristic scorer for Tic-Tac-Toe rule explanations.

    Checks whether key constraints appear in the model response.
    Returns a completeness score and number of missed constraints.
    """

    text = response.lower()

    constraints = {
        "grid": ["3x3", "3 x 3"],
        "players": ["two players"],
        "symbols": ["x", "o"],
        "turns": ["turn"],
        "win_condition": ["three in a row"],
        "draw_condition": ["draw", "board is full", "grid is filled"],
        "empty_spaces": ["empty", "unoccupied"]
    }

    matched = 0

    for phrases in constraints.values():
        if any(p in text for p in phrases):
            matched += 1

    total = len(constraints)

    score = matched / total
    missed = total - matched

    return {
        "rule_completeness_score": round(score, 2),
        "missed_constraints": missed
    }