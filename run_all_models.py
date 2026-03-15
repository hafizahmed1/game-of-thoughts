import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EXPERIMENTS = [
    "experiments/rule_understanding.py",
    "experiments/move_prediction.py",
    "experiments/multi_turn_simulation.py",
    "experiments/rule_errors.py",
    "experiments/game_generation.py",
]

PROVIDERS = ["gemini", "groq"]


def run_script(script_path: str, provider: str) -> bool:
    env = os.environ.copy()
    env["LLM_PROVIDER"] = provider

    print("\n" + "=" * 70)
    print(f"Running {script_path} with provider={provider}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(ROOT / script_path)],
        cwd=ROOT,
        env=env,
    )

    if result.returncode != 0:
        print(f"\nFAILED: {script_path} [{provider}]")
        return False

    print(f"\nDONE: {script_path} [{provider}]")
    return True


def main():
    failures = []

    for provider in PROVIDERS:
        for script in EXPERIMENTS:
            ok = run_script(script, provider)
            if not ok:
                failures.append((provider, script))

    print("\n" + "#" * 70)
    print("FINAL SUMMARY")
    print("#" * 70)

    if not failures:
        print("All experiments completed successfully for all providers.")
    else:
        print("Some runs failed:")
        for provider, script in failures:
            print(f"- provider={provider} | script={script}")

    print("\nExpected output files include:")
    print("results/tables/rule_understanding_summary_gemini.csv")
    print("results/tables/rule_understanding_summary_groq.csv")
    print("results/move_prediction_gemini.csv")
    print("results/move_prediction_groq.csv")
    print("results/tables/multi_turn_summary_gemini.csv")
    print("results/tables/multi_turn_summary_groq.csv")
    print("results/rule_error_detection_gemini.txt")
    print("results/rule_error_detection_groq.txt")
    print("results/game_generation_gemini.txt")
    print("results/game_generation_groq.txt")


if __name__ == "__main__":
    main()