from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.domain.entities.role import Role


class User(SQLModel, table=True):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)
    roles: List["Role"] = Relationship(back_populates="users")

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    udpated_at: Optional[datetime] = Field(default=None)


class UserCreate(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
