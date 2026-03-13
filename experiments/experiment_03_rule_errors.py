import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompts.templates import get_rule_error_detection_prompt
from src.utils.helpers import generate_text

BROKEN_RULES = """
Tic-Tac-Toe is played on a 3x3 grid.
Two players take turns placing X and O.
A player can place a mark anywhere.
The first player to place three marks in a row wins.
The game ends when the board is full.
"""

prompt = get_rule_error_detection_prompt(BROKEN_RULES)
response = generate_text(prompt)

print("BROKEN RULES:\n")
print(BROKEN_RULES)
print("\n" + "=" * 50 + "\n")
print("MODEL RESPONSE:\n")
print(response)

os.makedirs("results", exist_ok=True)
with open("results/experiment_03_output.txt", "w", encoding="utf-8") as f:
    f.write("BROKEN RULES:\n")
    f.write(BROKEN_RULES)
    f.write("\n\n" + "=" * 50 + "\n\n")
    f.write("MODEL RESPONSE:\n")
    f.write(response)