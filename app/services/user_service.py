from app.domain.entities.user import User, UserCreate
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


class UserService:
    """
    User Service
    """

    def __init__(self):
        self.user_repo = UserRepositoryImpl()

    def register_user(self, user_data: UserCreate) -> User:
        new_user = User(
            auth_id=user_data.auth_id,
            email=user_data.email,
            picture=user_data.picture,
        )

        return self.user_repo.create_user(user=new_user)

    def get_user(self, auth_id: str) -> User | None:
        return self.user_repo.get_user_by_id(auth_id)

    def list_users(self):
        return self.user_repo.get_all_users()
