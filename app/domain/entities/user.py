from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.users_roles import UsersRoles


if TYPE_CHECKING:
    from app.domain.entities.role import Role


class UserBase(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    roles: list["Role"] = Relationship(back_populates="roles", link_model=UsersRoles)

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    pass
