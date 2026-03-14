import pandas as pd

from src.data.game_loader import load_tictactoe_data
from src.prompts.templates import get_rule_explanation_prompt


def prepare_tictactoe_rule_understanding():
    data = load_tictactoe_data()
    conditions = data["conditions"]

    prompts = {
        name: get_rule_explanation_prompt(text)
        for name, text in conditions.items()
    }

    conditions_df = pd.DataFrame([
        {
            "condition": name,
            "num_lines": len(text.splitlines()),
            "num_chars": len(text),
        }
        for name, text in conditions.items()
    ])

    results_df = pd.DataFrame([
        {
            "condition": name,
            "prompt": prompt,
            "model_response": "",
            "rule_completeness_score": None,
            "invented_rules": None,
            "missed_constraints": None,
            "notes": "",
        }
        for name, prompt in prompts.items()
    ])

    return {
        "clean_rules": data["clean_rules"],
        "conditions_df": conditions_df,
        "prompts": prompts,
        "results_df": results_df,
    }