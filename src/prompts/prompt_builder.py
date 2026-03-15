def build_rule_understanding_prompt(game_name: str, rules_text: str) -> str:
    return f"""
You are given the rules of {game_name}.

Rules:
{rules_text}

Task:
Summarize the rules clearly and accurately.

Your answer should include:
1. Board or setup
2. Players
3. Legal turn action
4. Win condition
5. Draw or termination condition
""".strip()


def build_valid_move_prompt(
    game_name: str,
    rules_text: str,
    state_text: str,
    player: str,
) -> str:
    return f"""
You are given the rules of {game_name} and the current game state.

Rules:
{rules_text}

Current state:
{state_text}

Current player: {player}

Task:
Suggest exactly one valid move for the current player.

Return only the move.
""".strip()


def build_rule_error_detection_prompt(game_name: str, broken_rules_text: str) -> str:
    return f"""
You are given a possibly flawed rulebook for {game_name}.

Rules:
{broken_rules_text}

Task:
Identify inconsistencies, ambiguities, contradictions, or impossible rules.
Then suggest a corrected version.
""".strip()