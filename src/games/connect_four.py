from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.games.base_game import BaseGame


ROWS = 6
COLS = 7


@dataclass(frozen=True)
class ConnectFourState:
    board: list[list[str]]
    current_player: str


class ConnectFourGame(BaseGame):
    name = "connect_four"
    players = ["X", "O"]

    def initial_state(self) -> ConnectFourState:
        return ConnectFourState(
            board=[[" " for _ in range(COLS)] for _ in range(ROWS)],
            current_player="X",
        )

    def state_from_dict(self, data: dict) -> ConnectFourState:
        board = data["board"]
        current_player = data["current_player"]
        return ConnectFourState(board=board, current_player=current_player)

    def state_to_text(self, state: ConnectFourState) -> str:
        lines = ["Columns are 0-indexed.", "Board:"]
        for row in state.board:
            rendered = " | ".join(cell if cell != " " else "." for cell in row)
            lines.append(rendered)
        lines.append("0   1   2   3   4   5   6")
        lines.append(f"Current player: {state.current_player}")
        return "\n".join(lines)

    def parse_move(self, move_text: str) -> int:
        """
        Accepts formats like:
        - 3
        - column 3
        - col=3
        """
        cleaned = move_text.strip().lower()
        cleaned = cleaned.replace("column", "").replace("col", "").replace("=", " ")
        parts = [p for p in cleaned.split() if p]

        if len(parts) != 1:
            raise ValueError(f"Invalid Connect Four move format: {move_text!r}")

        try:
            return int(parts[0])
        except ValueError as exc:
            raise ValueError(f"Move must be a single integer column index: {move_text!r}") from exc

    def move_to_text(self, move: int) -> str:
        return str(move)

    def get_move_format_instructions(self) -> str:
        return (
            "Return only one move as a single integer column index.\n"
            "Columns are 0-indexed from 0 to 6.\n"
            "Example: 3"
        )

    def is_valid_move(self, state: ConnectFourState, move: int) -> bool:
        if not isinstance(move, int):
            return False
        if not (0 <= move < COLS):
            return False
        return state.board[0][move] == " "

    def get_legal_moves(self, state: ConnectFourState) -> Iterable[int]:
        return [c for c in range(COLS) if state.board[0][c] == " "]

    def apply_move(self, state: ConnectFourState, move: int) -> ConnectFourState:
        if not self.is_valid_move(state, move):
            raise ValueError(f"Invalid move for Connect Four: {move}")

        new_board = [row[:] for row in state.board]

        placed_row = None
        for r in range(ROWS - 1, -1, -1):
            if new_board[r][move] == " ":
                new_board[r][move] = state.current_player
                placed_row = r
                break

        if placed_row is None:
            raise ValueError(f"Could not place move in column {move}")

        next_player = "O" if state.current_player == "X" else "X"
        return ConnectFourState(board=new_board, current_player=next_player)

    def is_terminal(self, state: ConnectFourState) -> bool:
        return self.get_winner(state) is not None

    def get_winner(self, state: ConnectFourState) -> str | None:
        board = state.board

        def check_four(cells: list[str]) -> str | None:
            if cells[0] != " " and all(cell == cells[0] for cell in cells):
                return cells[0]
            return None

        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                winner = check_four([board[r][c + i] for i in range(4)])
                if winner:
                    return winner

        # Vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                winner = check_four([board[r + i][c] for i in range(4)])
                if winner:
                    return winner

        # Diagonal down-right
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                winner = check_four([board[r + i][c + i] for i in range(4)])
                if winner:
                    return winner

        # Diagonal up-right
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                winner = check_four([board[r - i][c + i] for i in range(4)])
                if winner:
                    return winner

        if all(board[0][c] != " " for c in range(COLS)):
            return "draw"

        return None
    def get_max_moves(self) -> int:
        return 42