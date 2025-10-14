from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.roles_permission import RolesPermissions

if TYPE_CHECKING:
    from app.domain.entities.role import Role


class PermissionBase(SQLModel):
    name: str = Field(unique=True)
    description: str | None = None
    resource: str  # e.g., "users", "orders", etc.
    action: str  # e.g., "create", "read", "update", "delete"


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    roles: list["Role"] = Relationship(
        back_populates="permissions", link_model=RolesPermissions
    )

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
