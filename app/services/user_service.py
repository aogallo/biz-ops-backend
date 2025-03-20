from app.domain.entities.user import User, UserCreate

from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class UserService:
    """
    Application Layer - User Bussines logic (Use Case)
    """

    def __init__(self, user_repo: UserRepositoryImpl):
        self.user_repo = user_repo

    def register_user(self, user_data: UserCreate) -> User:
        # hashed_password = bcrypt.hashpw(
        #     user_data.password.encode(), bcrypt.gensalt()
        # ).decode()

        new_user = User(
            auth_id=user_data.auth_id, email=user_data.email, picture=user_data.picture
        )

        return self.user_repo.create_user(new_user)

    def get_user(self, auth_id: str) -> User | None:
        return self.user_repo.get_user_by_id(auth_id)

    def list_users(self):
        return self.user_repo.get_all_users()
