from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.users_roles import UsersRoles

if TYPE_CHECKING:
    from app.domain.entities.role import Role


class UserBase(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: str | None = Field(default=None)


class User(UserBase, table=True):
    roles: list["Role"] = Relationship(
        back_populates="roles", link_model=UsersRoles
    )

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)


class UserCreate(UserBase):
    pass
