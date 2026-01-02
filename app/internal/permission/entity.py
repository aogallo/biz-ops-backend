"""Permission and Role entities for RBAC system."""
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.user.entity import User


class Permission(SQLModel, table=True):
    """
    System permissions for fine-grained access control.

    Permissions use the format: <resource>:<action>
    Examples: product:create, upload-sat-file:read, invoice:delete
    """

    __tablename__: ClassVar[str] = "permission"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module_name: str | None = Field(
        default=None, max_length=50, index=True
    )  # "inventory", "accounting", "sat", "crm"

    # Relationships
    roles: list["RolePermission"] = Relationship(back_populates="permission")


class Role(TimestampMixin, table=True):
    """
    User roles (admin, accountant, viewer, etc.).

    Roles are assigned to users via UserCompanyAccess.
    Each role has a set of permissions.
    """

    __tablename__: ClassVar[str] = "role"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    is_system: bool = Field(
        default=False
    )  # System roles cannot be deleted (admin, owner, etc.)

    # Relationships
    permissions: list["RolePermission"] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    """
    Many-to-many relationship between roles and permissions.

    Links roles to their associated permissions.
    """

    __tablename__: ClassVar[str] = "role_permission"

    role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permission.id", primary_key=True)

    # Relationships
    role: Role = Relationship(back_populates="permissions")
    permission: Permission = Relationship(back_populates="roles")


class UserPermission(SQLModel, table=True):
    """
    Direct permissions assigned to users (overrides role permissions).

    Allows granting or revoking specific permissions for individual users
    without changing their role.
    """

    __tablename__: ClassVar[str] = "user_permission"

    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permission.id", primary_key=True)
    granted: bool = Field(
        default=True
    )  # True = grant permission, False = revoke permission

    # Relationships
    user: "User" = Relationship()
    permission: Permission = Relationship()
