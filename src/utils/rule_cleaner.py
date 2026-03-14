def clean_core_rules(rulebook: dict) -> list[str]:
    """
    Clean extracted Tic-Tac-Toe rules.

    Fix known typos and remove title lines.
    """
    rules = rulebook["core_rules"].copy()

    cleaned = []

    for r in rules:

        # fix typo from errata
        r = r.replace("Player Twi", "Player Two")

        # remove title line
        if r.strip().upper() == "TIC TAC TOE RULES":
            continue

        cleaned.append(r)

    return cleaned