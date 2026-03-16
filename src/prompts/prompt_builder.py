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

def build_valid_move_prompt_baseline(
    game_name: str,
    rules_text: str,
    state_text: str,
    player: str,
) -> str:
    return f"""
Game: {game_name}

Rules:
{rules_text}

Current state:
{state_text}

Current player: {player}

Task:
Suggest exactly one valid move for the current player.

Return only the move coordinates.
Do not explain.
""".strip()


def build_valid_move_prompt_constrained(
    game_name: str,
    rules_text: str,
    state_text: str,
    player: str,
    legal_moves,
) -> str:
    legal_moves_text = "\n".join(str(move) for move in legal_moves)

    return f"""
Game: {game_name}

Rules:
{rules_text}

Current state:
{state_text}

Current player: {player}

Available legal moves:
{legal_moves_text}

Task:
Choose exactly one move from the list of legal moves.

Return only the move coordinates.
Do not explain.
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


def build_rule_error_detection_prompt(game_name: str, broken_rules_text: str) -> str:
    return f"""
You are given a possibly flawed rulebook for {game_name}.

Rules:
{broken_rules_text}

Task:
1. Identify missing, ambiguous, contradictory, or inconsistent rules.
2. Explain why each issue is problematic.
3. Suggest a corrected version of the rules.

Be specific and structured.
""".strip()

def build_game_generation_prompt(theme: str, constraints: str = "") -> str:
    return f"""
Design a new original board game.

Theme:
{theme}

Constraints:
{constraints}

Task:
Create a complete rule set for a playable game.

Your rule set should include:
1. Game title
2. Theme or concept
3. Number of players
4. Setup
5. Turn structure
6. Legal actions
7. Win condition
8. End condition

Make the rules clear, internally consistent, and playable.
""".strip()