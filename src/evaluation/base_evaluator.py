from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError