# Implement the repository interface using SQLModel
from typing import List, Optional
from sqlmodel import select
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, auth_id: str):
        result = await self.db.execute(select(User).where(User.auth_id == auth_id))
        return result.scalars().first()

    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars()._allrows()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
