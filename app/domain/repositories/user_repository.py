# Repository interface: Defines data access operations but has no DB dependencies
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import User
from app.infrastructure.repositories.base_repository import BaseRepository


class UserRepository(ABC, BaseRepository):
    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, auth_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass
