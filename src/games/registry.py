from src.games.tictactoe import TicTacToeGame


def create_game(game_slug: str, rules_text: str):
    if game_slug == "tictactoe":
        return TicTacToeGame(rules_text)
    raise ValueError(f"Unsupported game: {game_slug}")