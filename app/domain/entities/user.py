from typing import Optional, List
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from app.domain.entities.role import Role


class User(SQLModel, table=True):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)
    roles: List["Role"] = Relationship(back_populates="users")


class UserCreate(SQLModel):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)
