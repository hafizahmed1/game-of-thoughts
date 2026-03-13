import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompts.templates import get_rule_explanation_prompt
from src.utils.helpers import generate_text
from src.evaluation.metrics import rule_completeness_score

RULES = """
Tic-Tac-Toe is played on a 3x3 grid.
Two players alternate placing X and O.
Marks must be placed in empty cells.
Three marks in a row wins.
If the grid fills without a winner, the game is a draw.
"""

required_keywords = [
    "3x3 grid",
    "two players",
    "empty cell",
    "three",
    "draw"
]

prompt = get_rule_explanation_prompt(RULES)
response = generate_text(prompt)

score = rule_completeness_score(response, required_keywords)

print("PROMPT:\n")
print(prompt)
print("\n" + "=" * 50 + "\n")
print("MODEL RESPONSE:\n")
print(response)
print("\n" + "=" * 50 + "\n")
print(f"RULE COMPLETENESS SCORE: {score:.2f}")

os.makedirs("results", exist_ok=True)

with open("results/experiment_01_output.txt", "w", encoding="utf-8") as f:
    f.write("PROMPT:\n")
    f.write(prompt)
    f.write("\n\n" + "=" * 50 + "\n\n")
    f.write("MODEL RESPONSE:\n")
    f.write(response)
    f.write("\n\n" + "=" * 50 + "\n\n")
    f.write(f"RULE COMPLETENESS SCORE: {score:.2f}\n")