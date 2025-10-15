from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def create(self, model: T) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        pass

    @abstractmethod
    def update(self, id: int, model: T) -> T:
        """Update an existing entity"""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity by ID"""
        pass

    @abstractmethod
    def exists(self, id: int) -> bool:
        """Check if entity exists by ID"""
        pass
