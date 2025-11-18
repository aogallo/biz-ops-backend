# Repository interface:
# Defines data access operations but has no database dependencies
from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    """User repository interface"""

    @abstractmethod
    def create_user(self, user: User) -> User:
        """Create a user"""
        pass

    @abstractmethod
    def get_user_by_id(self, auth_id: str) -> User | None:
        """Get a user by id"""
        pass

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """Get all users"""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email"""
        pass
