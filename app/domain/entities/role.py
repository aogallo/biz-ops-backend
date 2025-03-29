from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.domain.entities.permission import Permission

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    permissions: List["Permission"] = Relationship(back_populates="roles")
    users: List["User"] = Relationship(back_populates="roles") 