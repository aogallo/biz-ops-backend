from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.domain.entities.role import Role


class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    resource: str  # e.g., "users", "orders", etc.
    action: str  # e.g., "create", "read", "update", "delete"
    roles: List["Role"] = Relationship(back_populates="permissions")

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    udpated_at: Optional[datetime] = Field(default=None)
