from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.games.base_game import BaseGame


@dataclass(frozen=True)
class TicTacToeState:
    board: list[list[str]]
    current_player: str


class TicTacToeGame(BaseGame):
    name = "tictactoe"
    players = ["X", "O"]

    def initial_state(self) -> TicTacToeState:
        return TicTacToeState(
            board=[[" " for _ in range(3)] for _ in range(3)],
            current_player="X",
        )

    def state_from_dict(self, data: dict) -> TicTacToeState:
        board = data["board"]
        current_player = data["current_player"]
        return TicTacToeState(board=board, current_player=current_player)

    def state_to_text(self, state: TicTacToeState) -> str:
        lines = ["Rows/Cols are 0-indexed.", "Board:"]
        for row_idx, row in enumerate(state.board):
            rendered = " | ".join(cell if cell != " " else "." for cell in row)
            lines.append(f"{row_idx}: {rendered}")
        lines.append("    0   1   2")
        lines.append(f"Current player: {state.current_player}")
        return "\n".join(lines)

    def parse_move(self, move_text: str) -> tuple[int, int]:
        """
        Accepts formats like:
        - (1, 2)
        - 1,2
        - 1 2
        """
        cleaned = move_text.strip()
        cleaned = cleaned.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        cleaned = cleaned.replace(",", " ")
        parts = [p for p in cleaned.split() if p]

        if len(parts) != 2:
            raise ValueError(f"Invalid Tic-Tac-Toe move format: {move_text!r}")

        try:
            row = int(parts[0])
            col = int(parts[1])
        except ValueError as exc:
            raise ValueError(f"Move must contain two integers: {move_text!r}") from exc

        return (row, col)

    def move_to_text(self, move: tuple[int, int]) -> str:
        row, col = move
        return f"({row}, {col})"

    def get_move_format_instructions(self) -> str:
        return (
            "Return only one move in the format: (row, col)\n"
            "Rows and columns are 0-indexed.\n"
            "Example: (1, 2)"
        )

    def is_valid_move(self, state: TicTacToeState, move: tuple[int, int]) -> bool:
        if not isinstance(move, tuple) or len(move) != 2:
            return False

        row, col = move
        if not isinstance(row, int) or not isinstance(col, int):
            return False

        if not (0 <= row < 3 and 0 <= col < 3):
            return False

        return state.board[row][col] == " "

    def get_legal_moves(self, state: TicTacToeState) -> Iterable[tuple[int, int]]:
        moves = []
        for r in range(3):
            for c in range(3):
                if state.board[r][c] == " ":
                    moves.append((r, c))
        return moves

    def apply_move(self, state: TicTacToeState, move: tuple[int, int]) -> TicTacToeState:
        if not self.is_valid_move(state, move):
            raise ValueError(f"Invalid move for Tic-Tac-Toe: {move}")

        row, col = move
        new_board = [r[:] for r in state.board]
        new_board[row][col] = state.current_player
        next_player = "O" if state.current_player == "X" else "X"

        return TicTacToeState(board=new_board, current_player=next_player)

    def is_terminal(self, state: TicTacToeState) -> bool:
        return self.get_winner(state) is not None

    def get_winner(self, state: TicTacToeState) -> str | None:
        board = state.board
        lines = []

        lines.extend(board)
        lines.extend([[board[0][c], board[1][c], board[2][c]] for c in range(3)])
        lines.append([board[0][0], board[1][1], board[2][2]])
        lines.append([board[0][2], board[1][1], board[2][0]])

        for line in lines:
            if line[0] != " " and line[0] == line[1] == line[2]:
                return line[0]

        if all(cell != " " for row in board for cell in row):
            return "draw"

        return None
    def get_max_moves(self) -> int:
        return 9