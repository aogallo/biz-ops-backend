# Repository interface: Defines data access operations but has no DB dependencies
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, auth_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> Sequence[User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass
