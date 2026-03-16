import os
import time
from dotenv import load_dotenv
from google import genai

from src.llm.gemini_model import GeminiModel
from src.llm.groq_model import GroqModel
from src.pipelines.rule_understanding import run_rule_understanding
from src.pipelines.move_prediction import simulate_multiple_turns
from src.pipelines.rule_error_detection import run_rule_error_detection
from src.pipelines.game_generation import run_game_generation


GAME_SLUG = "connect_four"
REQUEST_DELAY_SECONDS = 3.0


def pause():
    time.sleep(REQUEST_DELAY_SECONDS)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def run_for_model(model_label: str, model):
    print_header(f"{model_label} | {getattr(model, 'model_name', 'unknown')} | {GAME_SLUG}")

    # 1. Rule understanding
    print_header(f"{model_label} | RULE UNDERSTANDING | {GAME_SLUG}")
    ru = run_rule_understanding(GAME_SLUG, model)
    print(ru["response"])
    pause()

    # 2. Move prediction baseline
    print_header(f"{model_label} | MOVE PREDICTION | BASELINE | {GAME_SLUG}")
    mp_base = simulate_multiple_turns(
        game_slug=GAME_SLUG,
        model=model,
        max_turns=12,
        prompt_variant="baseline",
    )
    print("Attempted turns:", mp_base["attempted_turns"])
    print("Valid turns:", mp_base["valid_turns"])
    print("Valid turn rate:", mp_base["valid_turn_rate"])
    print("Winner:", mp_base["winner"])
    print("Terminal:", mp_base["terminal"])
    print("Final state:")
    print(mp_base["final_state"])
    pause()

    # 3. Move prediction constrained
    print_header(f"{model_label} | MOVE PREDICTION | CONSTRAINED | {GAME_SLUG}")
    mp_cons = simulate_multiple_turns(
        game_slug=GAME_SLUG,
        model=model,
        max_turns=12,
        prompt_variant="constrained",
    )
    print("Attempted turns:", mp_cons["attempted_turns"])
    print("Valid turns:", mp_cons["valid_turns"])
    print("Valid turn rate:", mp_cons["valid_turn_rate"])
    print("Winner:", mp_cons["winner"])
    print("Terminal:", mp_cons["terminal"])
    print("Final state:")
    print(mp_cons["final_state"])
    pause()

    # 4. Rule error detection
    print_header(f"{model_label} | RULE ERROR DETECTION | {GAME_SLUG}")
    red = run_rule_error_detection(GAME_SLUG, model)
    print(red["response"])
    pause()

    # 5. Game generation
    print_header(f"{model_label} | GAME GENERATION")
    gg = run_game_generation(
        model=model,
        theme="A competitive connection game inspired by climate resilience",
        constraints="The game should support 2 players and last about 15 minutes.",
    )
    print(gg["response"])
    pause()


def main():
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    gemini_model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
    groq_model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    print("Loaded GEMINI_MODEL =", gemini_model_name)
    print("Loaded GROQ_MODEL   =", groq_model_name)
    print("Gemini key loaded   =", "YES" if gemini_key else "NO")
    print("Groq key loaded     =", "YES" if groq_key else "NO")

    models = []

    if gemini_key:
        gemini_client = genai.Client(api_key=gemini_key)
        models.append((
            "Gemini",
            GeminiModel(client=gemini_client, model_name=gemini_model_name)
        ))

    if groq_key:
        models.append((
            "Groq",
            GroqModel(api_key=groq_key, model_name=groq_model_name)
        ))

    for model_label, model in models:
        try:
            run_for_model(model_label, model)
        except Exception as e:
            print_header(f"{model_label} FAILED")
            print(e)


if __name__ == "__main__":
    main()