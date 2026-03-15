from dataclasses import dataclass
from typing import List, Optional, Tuple
from src.games.base import BaseGame, GameState


@dataclass
class TicTacToeState(GameState):
    board: List[List[str]]


class TicTacToeGame(BaseGame):
    name = "Tic-Tac-Toe"
    slug = "tictactoe"

    def __init__(self, rules_text: str):
        self.rules_text = rules_text

    def get_rules_text(self) -> str:
        return self.rules_text

    def initial_state(self) -> TicTacToeState:
        return TicTacToeState(
            board=[[" " for _ in range(3)] for _ in range(3)],
            current_player="X"
        )

    def state_to_text(self, state: TicTacToeState) -> str:
        rows = []
        for row in state.board:
            rows.append(" | ".join(cell if cell != " " else "." for cell in row))
        return "\n".join(rows)

    def parse_move(self, raw_output: str) -> Tuple[int, int]:
        parts = raw_output.strip().replace(",", " ").split()
        if len(parts) < 2:
            raise ValueError("Could not parse move")
        return int(parts[0]), int(parts[1])

    def is_valid_move(self, state: TicTacToeState, move, player: str) -> bool:
        r, c = move
        return 0 <= r < 3 and 0 <= c < 3 and state.board[r][c] == " "

    def get_legal_moves(self, state: TicTacToeState, player: str):
        return [(r, c) for r in range(3) for c in range(3) if state.board[r][c] == " "]

    def apply_move(self, state: TicTacToeState, move, player: str) -> TicTacToeState:
        r, c = move
        new_board = [row[:] for row in state.board]
        new_board[r][c] = player
        next_player = "O" if player == "X" else "X"
        return TicTacToeState(board=new_board, current_player=next_player)

    def is_terminal(self, state: TicTacToeState) -> bool:
        return self.get_winner(state) is not None or all(
            cell != " " for row in state.board for cell in row
        )

    def get_winner(self, state: TicTacToeState) -> Optional[str]:
        board = state.board
        lines = []

        lines.extend(board)
        lines.extend([[board[r][c] for r in range(3)] for c in range(3)])
        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2-i] for i in range(3)])

        for line in lines:
            if line[0] != " " and line.count(line[0]) == 3:
                return line[0]
        return None