from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models.trace import Trace


ResultT = TypeVar("ResultT")


class Evaluator(ABC, Generic[ResultT]):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, trace: Trace) -> ResultT:
        pass