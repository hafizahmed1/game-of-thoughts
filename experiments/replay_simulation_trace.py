import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.games.registry import get_game


def replay_case(trace_path: str, case_id: str):
    with open(trace_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    case_data = None
    for item in data:
        if item["case_id"] == case_id:
            case_data = item
            break

    if case_data is None:
        raise ValueError(f"Case {case_id} not found")

    game = get_game(case_data["game"])

    print("\nINITIAL BOARD\n")
    print(case_data["initial_board"])

    state_texts = [turn["state_text_before"] for turn in case_data["turns"]]

    for i, turn in enumerate(case_data["turns"], start=1):
        print("\n" + "=" * 50)
        print(f"TURN {i}")
        print("=" * 50)
        print("Board before move:")
        print(turn["state_text_before"])
        print(f"Raw response: {turn['raw_response']}")
        print(f"Parsed move: {turn['parsed_move_text']}")
        print(f"Move valid: {turn['move_valid']}")

    print("\nFINAL BOARD\n")
    print(case_data["final_board"])
    print(f"\nStopped reason: {case_data['stopped_reason']}")
    print(f"Winner: {case_data['winner']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError(
            "Usage: python experiments/replay_simulation_trace.py <trace_json_path> <case_id>"
        )

    trace_path = sys.argv[1]
    case_id = sys.argv[2]
    replay_case(trace_path, case_id)