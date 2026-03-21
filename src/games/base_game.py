from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class BaseGame(ABC):
    """
    Base interface for all games.

    A concrete game class owns:
    - state representation
    - move parsing / formatting
    - validity rules
    - move application
    - terminal / winner logic
    """

    name: str = "base"
    players: list[str] = []
    
    @abstractmethod
    def get_max_moves(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def initial_state(self) -> Any:
        """Return the initial state for the game."""
        raise NotImplementedError

    @abstractmethod
    def state_from_dict(self, data: dict) -> Any:
        """Create a game state from serialized fixture data."""
        raise NotImplementedError

    @abstractmethod
    def state_to_text(self, state: Any) -> str:
        """Convert a state into a prompt-friendly text representation."""
        raise NotImplementedError

    @abstractmethod
    def parse_move(self, move_text: str) -> Any:
        """Parse raw model output into a game move object."""
        raise NotImplementedError

    @abstractmethod
    def move_to_text(self, move: Any) -> str:
        """Convert an internal move object to display text."""
        raise NotImplementedError

    @abstractmethod
    def get_move_format_instructions(self) -> str:
        """Return game-specific instructions describing expected move format."""
        raise NotImplementedError

    @abstractmethod
    def is_valid_move(self, state: Any, move: Any) -> bool:
        """Check whether a move is valid for the given state."""
        raise NotImplementedError

    @abstractmethod
    def get_legal_moves(self, state: Any) -> Iterable[Any]:
        """Return all legal moves for the given state."""
        raise NotImplementedError

    @abstractmethod
    def apply_move(self, state: Any, move: Any) -> Any:
        """Return the next state after applying the move."""
        raise NotImplementedError

    @abstractmethod
    def is_terminal(self, state: Any) -> bool:
        """Return True if the state is terminal."""
        raise NotImplementedError

    @abstractmethod
    def get_winner(self, state: Any) -> str | None:
        """
        Return:
        - player symbol/name if there is a winner
        - 'draw' for a draw
        - None if game is still ongoing
        """
        raise NotImplementedError