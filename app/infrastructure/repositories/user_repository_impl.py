from sqlmodel import Session, select

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database import get_current_session


class UserRepositoryImpl(UserRepository):
    """Implementation of User Repository"""

    def __init__(self, session: Session | None = None) -> None:
        self.db = session or get_current_session()

    def create_user(self, user: User) -> User:
        """Create a new user"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, auth_id: str) -> User | None:
        """Get a user by id"""
        statement = select(User).where(User.auth_id == auth_id)
        result = self.db.exec(statement=statement)
        user: User | None = result.first()
        return user

    def get_all_users(self) -> list[User]:
        """Get all users"""
        result = list(self.db.exec(select(User)))
        return result

    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email"""
        result = self.db.exec(select(User).where(User.email == email))
        user: User | None = result.first()
        return user
