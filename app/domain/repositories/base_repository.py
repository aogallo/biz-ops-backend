from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, model: T) -> T:
        pass

    @abstractmethod
    def update(self, id: int, new: T) -> T:
        pass
