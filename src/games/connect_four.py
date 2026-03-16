from dataclasses import dataclass
from typing import List, Optional

from src.games.base import BaseGame, GameState


@dataclass
class ConnectFourState(GameState):
    board: List[List[str]]


class ConnectFourGame(BaseGame):
    name = "Connect Four"
    slug = "connect_four"

    def __init__(self, rules_text: str):
        self.rules_text = rules_text

    def get_rules_text(self) -> str:
        return self.rules_text

    def get_rules_summary(self) -> str:
        return (
            "Connect Four rules:\n"
            "- The board is 6 rows by 7 columns.\n"
            "- Two players alternate turns: X then O.\n"
            "- On a turn, a player chooses one column.\n"
            "- The piece falls to the lowest empty space in that column.\n"
            "- A player wins by getting 4 marks in a row horizontally, vertically, or diagonally.\n"
            "- If the board is full and nobody has 4 in a row, the game is a draw."
        )

    def initial_state(self) -> ConnectFourState:
        return ConnectFourState(
            board=[[" " for _ in range(7)] for _ in range(6)],
            current_player="X",
        )

    def state_to_text(self, state: ConnectFourState) -> str:
        rows = []
        for row in state.board:
            rows.append(" | ".join(cell if cell != " " else "." for cell in row))
        rows.append("0 | 1 | 2 | 3 | 4 | 5 | 6")
        return "\n".join(rows)

    def parse_move(self, raw_output: str) -> int:
        cleaned = (
            raw_output.strip()
            .replace("(", " ")
            .replace(")", " ")
            .replace(",", " ")
        )
        parts = cleaned.split()

        for part in parts:
            if part.lstrip("-").isdigit():
                return int(part)

        raise ValueError(f"Could not parse move from: {raw_output}")

    def is_valid_move(self, state: ConnectFourState, move, player: str) -> bool:
        if not isinstance(move, int):
            return False
        if not (0 <= move < 7):
            return False
        return state.board[0][move] == " "

    def get_legal_moves(self, state: ConnectFourState, player: str):
        return [c for c in range(7) if state.board[0][c] == " "]

    def apply_move(self, state: ConnectFourState, move, player: str) -> ConnectFourState:
        if not self.is_valid_move(state, move, player):
            raise ValueError(f"Invalid move {move} for player {player}")

        new_board = [row[:] for row in state.board]

        for r in range(5, -1, -1):
            if new_board[r][move] == " ":
                new_board[r][move] = player
                break

        next_player = "O" if player == "X" else "X"
        return ConnectFourState(board=new_board, current_player=next_player)

    def is_terminal(self, state: ConnectFourState) -> bool:
        return self.get_winner(state) is not None or all(
            cell != " " for row in state.board for cell in row
        )

    def get_winner(self, state: ConnectFourState) -> Optional[str]:
        board = state.board
        rows, cols = 6, 7

        for r in range(rows):
            for c in range(cols):
                player = board[r][c]
                if player == " ":
                    continue

                # Horizontal
                if c <= cols - 4 and all(board[r][c + i] == player for i in range(4)):
                    return player

                # Vertical
                if r <= rows - 4 and all(board[r + i][c] == player for i in range(4)):
                    return player

                # Diagonal down-right
                if r <= rows - 4 and c <= cols - 4 and all(board[r + i][c + i] == player for i in range(4)):
                    return player

                # Diagonal down-left
                if r <= rows - 4 and c >= 3 and all(board[r + i][c - i] == player for i in range(4)):
                    return player

        return None