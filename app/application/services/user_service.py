from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

from app.presentation.schemas.user import UserCreate


class UserService:
    """
    Application Layer - User Bussines logic (Use Case)
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserCreate) -> User:
        # hashed_password = bcrypt.hashpw(
        #     user_data.password.encode(), bcrypt.gensalt()
        # ).decode()

        new_user = User(
            auth_id=user_data.auth_id, email=user_data.email, picture=user_data.picture
        )

        return await self.user_repo.create_user(new_user)

    async def get_user(self, auth_id: str) -> User | None:
        return await self.user_repo.get_user_by_id(auth_id)
