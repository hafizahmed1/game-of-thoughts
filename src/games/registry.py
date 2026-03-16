from src.games.tictactoe import TicTacToeGame
from src.games.connect_four import ConnectFourGame
from src.games.nim import NimGame


def create_game(game_slug: str, rules_text: str):
    if game_slug == "tictactoe":
        return TicTacToeGame(rules_text)
    if game_slug == "connect_four":
        return ConnectFourGame(rules_text)
    if game_slug == "nim":
        return NimGame(rules_text)

    raise ValueError(f"Unsupported game slug: {game_slug}")