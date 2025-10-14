# Implement the repository interface using SQLModel
from typing import Optional, List
from sqlmodel import select
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.repositories.base_repository import BaseRepository


class UserRepositoryImpl(UserRepository):
    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        return user

    def get_user_by_id(self, auth_id: str):
        result = self.db.exec(select(User).where(User.auth_id == auth_id))
        return result.first()

    def get_all_users(self):
        result = list(self.db.exec(select(User)))
        return result

    def get_user_by_email(self, email: str) -> Optional[User]:
        result = self.db.exec(select(User).where(User.email == email))
        return result.first()


def get_user_repository() -> UserRepository:
    return UserRepositoryImpl()
