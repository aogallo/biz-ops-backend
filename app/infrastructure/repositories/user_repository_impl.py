# Implement the repository interface using SQLModel
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.db.close()
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
