from __future__ import annotations

from src.games.base_game import BaseGame
from src.games.connect_four import ConnectFourGame
from src.games.tictactoe import TicTacToeGame


GAME_REGISTRY: dict[str, type[BaseGame]] = {
    "tictactoe": TicTacToeGame,
    "connect_four": ConnectFourGame,
}


def get_game(game_slug: str) -> BaseGame:
    try:
        game_cls = GAME_REGISTRY[game_slug]
    except KeyError as exc:
        supported = ", ".join(sorted(GAME_REGISTRY.keys()))
        raise ValueError(f"Unsupported game '{game_slug}'. Supported games: {supported}") from exc

    return game_cls()