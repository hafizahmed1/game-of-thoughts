import sys
from pathlib import Path

# -------------------------------------------------
# Setup project root so src imports work
# -------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -------------------------------------------------
# Imports
# -------------------------------------------------
from src.prompts.templates import get_game_generation_prompt
from src.utils.helpers import generate_text


def main():

    theme = "a simple two-player strategy board game about collecting treasure"

    prompt = get_game_generation_prompt(theme)

    response = generate_text(prompt)

    print("\nPROMPT\n")
    print(prompt)

    print("\n" + "=" * 60 + "\n")

    print("MODEL RESPONSE\n")
    print(response)

    # -------------------------------------------------
    # Save results
    # -------------------------------------------------
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / "game_generation.txt"

    with open(output_path, "w", encoding="utf-8") as f:

        f.write("PROMPT\n")
        f.write(prompt)

        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("MODEL RESPONSE\n")
        f.write(response)

    print("\nSaved results to:", output_path)


if __name__ == "__main__":
    main()