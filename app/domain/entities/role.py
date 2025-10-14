from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.domain.entities.roles_permission import RolesPermissions

if TYPE_CHECKING:
    from app.domain.entities.permission import Permission


class RoleBase(SQLModel):
    name: str = Field(unique=True)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    permissions: list["Permission"] = Relationship(
        back_populates="roles", link_model=RolesPermissions
    )

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)
