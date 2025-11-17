from sqlmodel import Session, select

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database import get_current_session


class UserRepositoryImpl(UserRepository):
    """Implementation of UserRepository interface."""

    def __init__(self, session: Session | None = None) -> None:
        # Use provided session or get from context
        self.db = session or get_current_session()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, auth_id: str) -> User | None:
        result = self.db.exec(select(User).where(User.auth_id == auth_id))
        return result.first()

    def get_all_users(self) -> list[User]:
        result = list(self.db.exec(select(User)))
        return result

    def get_user_by_email(self, email: str) -> User | None:
        result = self.db.exec(select(User).where(User.email == email))
        return result.first()
