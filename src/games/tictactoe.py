
class TicTacToe:
    def __init__(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"

    def make_move(self, row, col):
        if self.board[row][col] != " ":
            return False
        self.board[row][col] = self.current_player
        return True

    def switch_player(self):
        if self.current_player == "X":
            self.current_player = "O"
        else:
            self.current_player = "X"

    def is_valid_move(self, row, col):
        return (
            0 <= row < 3 and
            0 <= col < 3 and
            self.board[row][col] == " "
        )

    def board_to_text(self):
        rows = []
        for row in self.board:
            rows.append(" | ".join(cell if cell != " " else "-" for cell in row))
        return "\n".join(rows)