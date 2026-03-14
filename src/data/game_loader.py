import json
from pathlib import Path

from src.utils.rule_cleaner import clean_core_rules


def find_project_root():
    root = Path.cwd()
    while not (root / "src").exists() and root != root.parent:
        root = root.parent
    return root


def load_tictactoe_data():

    root = find_project_root()

    rulebook_path = root / "data" / "processed" / "tictactoe_rulebook.json"
    broken_path = root / "data" / "processed" / "broken_tic_tac_toe.txt"

    rulebook = json.loads(rulebook_path.read_text())

    broken_rules = broken_path.read_text()

    clean_rules = clean_core_rules(rulebook)

    return {
        "rulebook": rulebook,
        "clean_rules": clean_rules,
        "conditions": {
            "clean": "\n".join(clean_rules),
            "raw": rulebook["raw_text"],
            "broken": broken_rules,
        },
    }