from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class BaseRepository[T](ABC):
    @abstractmethod
    def create(self, model: T) -> T:
        pass

    @abstractmethod
    def update(self, id: int, new: T) -> T:
        pass
