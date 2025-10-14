from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.roles_permission import RolesPermissions

if TYPE_CHECKING:
    from app.domain.entities.permission import Permission


class RoleBase(SQLModel):
    name: str = Field(unique=True)
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    permissions: list["Permission"] = Relationship(
        back_populates="roles", link_model=RolesPermissions
    )

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
