import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompts.templates import get_valid_move_prompt
from src.utils.helpers import generate_text
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
    {
        "board": [
            ["X", "X", " "],
            [" ", "O", " "],
            [" ", " ", " "]
        ],
        "player": "O"
    },
    {
        "board": [
            ["X", " ", " "],
            ["O", "X", " "],
            [" ", " ", "O"]
        ],
        "player": "X"
    },
    {
        "board": [
            ["O", "X", "O"],
            ["X", " ", " "],
            [" ", " ", "X"]
        ],
        "player": "O"
    },
    {
        "board": [
            ["X", "O", "X"],
            ["O", "X", " "],
            [" ", " ", "O"]
        ],
        "player": "X"
    },
    {
        "board": [
            [" ", " ", " "],
            [" ", "X", " "],
            [" ", " ", "O"]
        ],
        "player": "X"
    },
    {
        "board": [
            ["X", "O", " "],
            [" ", "O", "X"],
            [" ", " ", " "]
        ],
        "player": "X"
    },
    {
        "board": [
            ["X", " ", "O"],
            [" ", "X", " "],
            ["O", " ", " "]
        ],
        "player": "O"
    },
    {
        "board": [
            [" ", "O", " "],
            ["X", " ", "X"],
            [" ", " ", "O"]
        ],
        "player": "X"
    },
    {
        "board": [
            ["X", " ", " "],
            [" ", "O", " "],
            [" ", " ", "X"]
        ],
        "player": "O"
    },
    {
        "board": [
            ["O", " ", "X"],
            [" ", "X", " "],
            [" ", "O", " "]
        ],
        "player": "O"
    }
]


def board_to_text(board):
    rows = []
    for row in board:
        rows.append(" | ".join(cell if cell != " " else "-" for cell in row))
    return "\n".join(rows)


def make_game_from_board(board, player):
    game = TicTacToe()
    game.board = board
    game.current_player = player
    return game


def main():
    os.makedirs("results", exist_ok=True)

    csv_path = "results/experiment_02b_results.csv"
    total = len(TEST_CASES)
    valid_count = 0
    parsed_count = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "test_id",
            "player",
            "board_text",
            "model_response",
            "parsed_move",
            "is_valid"
        ])

        for i, case in enumerate(TEST_CASES, start=1):
            board = case["board"]
            player = case["player"]

            game = make_game_from_board(board, player)
            board_text = board_to_text(board)

            prompt = get_valid_move_prompt(RULES, board_text, player)
            response = generate_text(prompt)
            move = parse_move(response)

            is_valid = False
            parsed_move_text = ""

            if move is not None:
                parsed_count += 1
                row, col = move
                parsed_move_text = f"({row}, {col})"
                is_valid = game.is_valid_move(row, col)

                if is_valid:
                    valid_count += 1

            writer.writerow([
                i,
                player,
                board_text,
                response,
                parsed_move_text,
                is_valid
            ])

            print(f"Test {i}")
            print(board_text)
            print("Response:", response)
            print("Parsed:", parsed_move_text if parsed_move_text else "None")
            print("Valid:", is_valid)
            print("-" * 50)

    print("\nSUMMARY")
    print(f"Total tests: {total}")
    print(f"Parsed moves: {parsed_count}/{total}")
    print(f"Valid moves: {valid_count}/{total}")
    print(f"Valid move rate: {valid_count / total:.2f}")


if __name__ == "__main__":
    main()