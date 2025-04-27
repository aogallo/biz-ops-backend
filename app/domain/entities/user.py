from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)


class User(UserBase, table=True):
    pass


class UserCreate(UserBase):
    pass
