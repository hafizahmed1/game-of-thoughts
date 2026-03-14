import sys
import os
import csv

# allow importing from src/
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
    {"board": [["X","X"," "],[" ","O"," "],[" "," "," "]], "player":"O"},
    {"board": [["X"," "," "],["O","X"," "],[" "," ","O"]], "player":"X"},
    {"board": [["O","X","O"],["X"," "," "],[" "," ","X"]], "player":"O"},
    {"board": [["X","O","X"],["O","X"," "],[" "," ","O"]], "player":"X"},
    {"board": [[" "," "," "],[" ","X"," "],[" "," ","O"]], "player":"X"},
    {"board": [["X","O"," "],[" ","O","X"],[" "," "," "]], "player":"X"},
    {"board": [["X"," ","O"],[" ","X"," "],["O"," "," "]], "player":"O"},
    {"board": [[" ","O"," "],["X"," ","X"],[" "," ","O"]], "player":"X"},
    {"board": [["X"," "," "],[" ","O"," "],[" "," ","X"]], "player":"O"},
    {"board": [["O"," ","X"],[" ","X"," "],[" ","O"," "]], "player":"O"},
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
    """
    Check if the given player has three in a row.
    """
    lines = []

    # rows
    lines.extend(board)

    # columns
    lines.extend([[board[r][c] for r in range(3)] for c in range(3)])

    # diagonals
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])

    return any(all(cell == player for cell in line) for line in lines)


def is_winning_move(game, row, col, player):
    """
    Check if placing a mark here wins immediately.
    """
    if not game.is_valid_move(row, col):
        return False

    temp_board = [r[:] for r in game.board]
    temp_board[row][col] = player

    return check_winner(temp_board, player)

def main():

    os.makedirs("results", exist_ok=True)

    csv_path = "results/tables/move_prediction_results.csv"

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

            response = generate_text(prompt)

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

            print(f"\nTest {i}")
            print(board_text)
            print("Response:", response)
            print("Parsed:", parsed_move_text if parsed_move_text else "None")
            print("Valid:", is_valid)
            print("Optimal:", is_optimal)
            print("-" * 50)

    valid_rate = valid_count / total if total else 0
    optimal_rate = optimal_count / total if total else 0

    print("\nSUMMARY")
    print("Total tests:", total)
    print("Parsed moves:", parsed_count)
    print("Valid moves:", valid_count)
    print("Valid move rate:", round(valid_rate, 2))
    print("Optimal moves:", optimal_count)
    print("Optimal move rate:", round(optimal_rate, 2))

    print("\nSaved results to:", csv_path)


if __name__ == "__main__":
    main()