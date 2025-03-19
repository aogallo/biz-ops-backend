# SQL Models Maps to a database table
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    auth_id: str = Field(primary_key=True)
    email: EmailStr
    picture: Optional[str] = Field(default=None)
