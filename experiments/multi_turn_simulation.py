import sys
import time
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.prompts.templates import get_valid_move_prompt
from src.utils.helpers import generate_text, get_provider
from src.evaluation.metrics import parse_move
from src.games.tictactoe import TicTacToe


RULES = """
Tic-Tac-Toe is played on a 3x3 grid.
Two players alternate placing X and O.
Marks must be placed in empty cells.
Three marks in a row wins.
If the grid fills without a winner, the game is a draw.
"""

START_CASES = [
    {
        "name": "midgame_1",
        "board": [
            ["X", "O", " "],
            [" ", "X", " "],
            ["O", " ", " "]
        ],
        "player": "O",
        "max_turns": 4
    },
    {
        "name": "midgame_2",
        "board": [
            ["X", " ", " "],
            [" ", "O", " "],
            [" ", " ", "X"]
        ],
        "player": "O",
        "max_turns": 4
    },
    {
        "name": "midgame_3",
        "board": [
            ["X", "O", "X"],
            [" ", "O", " "],
            [" ", " ", " "]
        ],
        "player": "X",
        "max_turns": 3
    },
    {
        "name": "midgame_4",
        "board": [
            ["X", " ", "O"],
            [" ", "X", " "],
            [" ", " ", "O"]
        ],
        "player": "X",
        "max_turns": 4
    },
    {
        "name": "midgame_5",
        "board": [
            ["O", "X", " "],
            [" ", "O", " "],
            ["X", " ", " "]
        ],
        "player": "X",
        "max_turns": 4
    },
    {
        "name": "midgame_6",
        "board": [
            ["X", "O", " "],
            ["X", " ", "O"],
            [" ", " ", " "]
        ],
        "player": "X",
        "max_turns": 4
    },
    {
        "name": "midgame_7",
        "board": [
            [" ", "X", " "],
            ["O", "X", " "],
            [" ", "O", " "]
        ],
        "player": "O",
        "max_turns": 4
    },
    {
        "name": "midgame_8",
        "board": [
            ["O", " ", "X"],
            [" ", "X", " "],
            [" ", "O", " "]
        ],
        "player": "O",
        "max_turns": 4
    },
    {
        "name": "midgame_9",
        "board": [
            ["X", " ", " "],
            ["O", "X", " "],
            [" ", " ", "O"]
        ],
        "player": "X",
        "max_turns": 4
    },
    {
        "name": "midgame_10",
        "board": [
            [" ", "O", "X"],
            [" ", "X", " "],
            ["O", " ", " "]
        ],
        "player": "O",
        "max_turns": 4
    }
]


def board_to_text(board):
    rows = []
    for row in board:
        rows.append(" | ".join(cell if cell != " " else "-" for cell in row))
    return "\n".join(rows)


def other_player(p):
    return "O" if p == "X" else "X"


def check_winner(board, player):
    lines = []
    lines.extend(board)
    lines.extend([[board[r][c] for r in range(3)] for c in range(3)])
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])
    return any(all(c == player for c in line) for line in lines)


def board_full(board):
    return all(cell != " " for row in board for cell in row)


def generate_with_retry(prompt, provider):
    if provider == "gemini":
        time.sleep(5)

    while True:
        try:
            return generate_text(prompt)
        except Exception as e:
            if provider == "gemini" and ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)):
                print("Rate limit hit. Waiting 15 seconds...")
                time.sleep(15)
            else:
                raise


def run_case(case, provider):
    board = [r[:] for r in case["board"]]
    player = case["player"]
    max_turns = case["max_turns"]

    logs = []
    valid_turns = 0

    for t in range(1, max_turns + 1):
        if check_winner(board, "X") or check_winner(board, "O") or board_full(board):
            break

        board_text = board_to_text(board)
        prompt = get_valid_move_prompt(RULES, board_text, player)
        response = generate_with_retry(prompt, provider)
        move = parse_move(response)

        parsed = ""
        is_valid = False

        if move is not None:
            r, c = move
            parsed = f"({r},{c})"

            game = TicTacToe()
            game.board = [row[:] for row in board]

            is_valid = game.is_valid_move(r, c)

            if is_valid:
                board[r][c] = player
                valid_turns += 1

        logs.append({
            "turn": t,
            "player": player,
            "board_before": board_text,
            "response": response,
            "parsed": parsed,
            "valid": is_valid
        })

        if not is_valid:
            break

        if check_winner(board, player) or board_full(board):
            break

        player = other_player(player)

    total_turns = len(logs)
    coherence = valid_turns / total_turns if total_turns else 0

    winner = None
    if check_winner(board, "X"):
        winner = "X"
    elif check_winner(board, "O"):
        winner = "O"

    return {
        "name": case["name"],
        "total_turns": total_turns,
        "valid_turns": valid_turns,
        "coherence_rate": round(coherence, 2),
        "winner": winner,
        "final_board": board_to_text(board),
        "logs": logs
    }


def save_text(results, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"CASE: {r['name']}\n")
            f.write(f"Total turns: {r['total_turns']}\n")
            f.write(f"Valid turns: {r['valid_turns']}\n")
            f.write(f"Coherence rate: {r['coherence_rate']}\n")
            f.write(f"Winner: {r['winner']}\n")
            f.write("Final board:\n")
            f.write(r["final_board"])
            f.write("\n\n")
            f.write("=" * 60 + "\n\n")

            for log in r["logs"]:
                f.write(f"Turn {log['turn']} | Player: {log['player']}\n")
                f.write("Board before:\n")
                f.write(log["board_before"] + "\n\n")
                f.write("Model response:\n")
                f.write(log["response"] + "\n\n")
                f.write(f"Parsed move: {log['parsed']}\n")
                f.write(f"Valid: {log['valid']}\n")
                f.write("\n" + "-" * 50 + "\n\n")


def save_csv(results, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case",
                "total_turns",
                "valid_turns",
                "coherence_rate",
                "winner"
            ]
        )
        writer.writeheader()

        for r in results:
            writer.writerow({
                "case": r["name"],
                "total_turns": r["total_turns"],
                "valid_turns": r["valid_turns"],
                "coherence_rate": r["coherence_rate"],
                "winner": r["winner"]
            })


def main():
    provider = get_provider()
    results = []

    for case in START_CASES:
        print("Running:", case["name"], f"[{provider}]")
        result = run_case(case, provider)
        results.append(result)

    text_path = ROOT / "results" / f"multi_turn_simulation_{provider}.txt"
    csv_path = ROOT / "results" / "tables" / f"multi_turn_summary_{provider}.csv"

    save_text(results, text_path)
    save_csv(results, csv_path)

    print("\nSaved:")
    print(text_path)
    print(csv_path)


if __name__ == "__main__":
    main()