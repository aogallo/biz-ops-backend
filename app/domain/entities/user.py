from datetime import UTC, datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: str | None = Field(default=None)


class User(UserBase, table=True):
    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)


class UserCreate(UserBase):
    pass
