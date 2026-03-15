import sys
import csv
import time
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

TEST_CASES = [
    {"board": [["X", "X", " "], [" ", "O", " "], [" ", " ", " "]], "player": "O"},
    {"board": [["X", " ", " "], ["O", "X", " "], [" ", " ", "O"]], "player": "X"},
    {"board": [["O", "X", "O"], ["X", " ", " "], [" ", " ", "X"]], "player": "O"},
    {"board": [["X", "O", "X"], ["O", "X", " "], [" ", " ", "O"]], "player": "X"},
    {"board": [[" ", " ", " "], [" ", "X", " "], [" ", " ", "O"]], "player": "X"},
    {"board": [["X", "O", " "], [" ", "O", "X"], [" ", " ", " "]], "player": "X"},
    {"board": [["X", " ", "O"], [" ", "X", " "], ["O", " ", " "]], "player": "O"},
    {"board": [[" ", "O", " "], ["X", " ", "X"], [" ", " ", "O"]], "player": "X"},
    {"board": [["X", " ", " "], [" ", "O", " "], [" ", " ", "X"]], "player": "O"},
    {"board": [["O", " ", "X"], [" ", "X", " "], [" ", "O", " "]], "player": "O"},
    {"board": [["X", "X", " "], ["O", " ", " "], [" ", " ", "O"]], "player": "O"},
    {"board": [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]], "player": "X"},
    {"board": [["X", " ", "X"], ["O", "O", " "], [" ", " ", " "]], "player": "X"},
    {"board": [[" ", " ", " "], ["X", "O", " "], [" ", " ", " "]], "player": "X"},
    {"board": [["O", " ", " "], [" ", "X", " "], [" ", " ", "O"]], "player": "X"},
    {"board": [["X", "O", "X"], [" ", "O", " "], [" ", " ", " "]], "player": "X"},
    {"board": [[" ", "X", " "], ["O", "O", "X"], [" ", " ", " "]], "player": "O"},
    {"board": [["X", " ", " "], [" ", "O", "X"], [" ", " ", "O"]], "player": "X"},
    {"board": [["O", "X", " "], [" ", "O", " "], [" ", " ", "X"]], "player": "O"},
    {"board": [[" ", " ", " "], [" ", "X", "O"], [" ", " ", "X"]], "player": "O"},
]


def board_to_text(board):
    rows = []
    for row in board:
        rows.append(" | ".join(cell if cell != " " else "-" for cell in row))
    return "\n".join(rows)


def make_game_from_board(board, player):
    game = TicTacToe()
    game.board = [r[:] for r in board]
    game.current_player = player
    return game


def check_winner(board, player):
    lines = []
    lines.extend(board)
    lines.extend([[board[r][c] for r in range(3)] for c in range(3)])
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])
    return any(all(cell == player for cell in line) for line in lines)


def is_winning_move(game, row, col, player):
    if not game.is_valid_move(row, col):
        return False

    temp_board = [r[:] for r in game.board]
    temp_board[row][col] = player
    return check_winner(temp_board, player)


def generate_text_with_retry(prompt, provider, base_delay=5, retry_delay=15):
    if provider == "gemini":
        time.sleep(base_delay)

    while True:
        try:
            return generate_text(prompt)
        except Exception as e:
            msg = str(e)
            if provider == "gemini" and ("429" in msg or "RESOURCE_EXHAUSTED" in msg):
                print(f"Rate limit hit. Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)
            else:
                raise


def main():
    provider = get_provider()

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    csv_path = results_dir / f"move_prediction_{provider}.csv"

    total = len(TEST_CASES)
    parsed_count = 0
    valid_count = 0
    optimal_count = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "test_id",
            "player",
            "board_text",
            "model_response",
            "parsed_move",
            "is_valid",
            "is_optimal"
        ])

        for i, case in enumerate(TEST_CASES, start=1):
            board = case["board"]
            player = case["player"]

            game = make_game_from_board(board, player)
            board_text = board_to_text(board)
            prompt = get_valid_move_prompt(RULES, board_text, player)

            response = generate_text_with_retry(prompt, provider)
            move = parse_move(response)

            parsed_move_text = ""
            is_valid = False
            is_optimal = False

            if move is not None:
                parsed_count += 1

                row, col = move
                parsed_move_text = f"({row},{col})"

                is_valid = game.is_valid_move(row, col)

                if is_valid:
                    valid_count += 1

                    if is_winning_move(game, row, col, player):
                        optimal_count += 1
                        is_optimal = True

            writer.writerow([
                i,
                player,
                board_text,
                response,
                parsed_move_text,
                is_valid,
                is_optimal
            ])

            print(f"\nTest {i} [{provider}]")
            print(board_text)
            print("Response:", response)
            print("Parsed:", parsed_move_text if parsed_move_text else "None")
            print("Valid:", is_valid)
            print("Optimal:", is_optimal)
            print("-" * 50)

    valid_rate = valid_count / total if total else 0
    optimal_rate = optimal_count / total if total else 0
    parsed_rate = parsed_count / total if total else 0

    print("\nSUMMARY")
    print("Provider:", provider)
    print("Total tests:", total)
    print("Parsed moves:", parsed_count)
    print("Parsed move rate:", round(parsed_rate, 2))
    print("Valid moves:", valid_count)
    print("Valid move rate:", round(valid_rate, 2))
    print("Optimal moves:", optimal_count)
    print("Optimal move rate:", round(optimal_rate, 2))
    print("\nSaved results to:", csv_path)


if __name__ == "__main__":
    main()