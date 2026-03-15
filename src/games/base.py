from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class GameState:
    current_player: str


class BaseGame(ABC):
    name: str
    slug: str

    @abstractmethod
    def get_rules_text(self) -> str:
        pass

    @abstractmethod
    def initial_state(self) -> GameState:
        pass

    @abstractmethod
    def state_to_text(self, state: GameState) -> str:
        pass

    @abstractmethod
    def parse_move(self, raw_output: str) -> Any:
        pass

    @abstractmethod
    def is_valid_move(self, state: GameState, move: Any, player: str) -> bool:
        pass

    @abstractmethod
    def get_legal_moves(self, state: GameState, player: str) -> List[Any]:
        pass

    @abstractmethod
    def apply_move(self, state: GameState, move: Any, player: str) -> GameState:
        pass

    @abstractmethod
    def is_terminal(self, state: GameState) -> bool:
        pass

    @abstractmethod
    def get_winner(self, state: GameState) -> Optional[str]:
        pass