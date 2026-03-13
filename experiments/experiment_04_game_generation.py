import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompts.templates import get_game_generation_prompt
from src.utils.helpers import generate_text

theme = "a simple two-player strategy board game about collecting treasure"

prompt = get_game_generation_prompt(theme)
response = generate_text(prompt)

print("PROMPT:\n")
print(prompt)
print("\n" + "=" * 50 + "\n")
print("MODEL RESPONSE:\n")
print(response)

os.makedirs("results", exist_ok=True)
with open("results/experiment_04_output.txt", "w", encoding="utf-8") as f:
    f.write("PROMPT:\n")
    f.write(prompt)
    f.write("\n\n" + "=" * 50 + "\n\n")
    f.write("MODEL RESPONSE:\n")
    f.write(response)