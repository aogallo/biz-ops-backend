"""Concrete implementation of Permission repository using SQLModel."""

from uuid import UUID

from sqlmodel import Session, select

from app.internal.permission.entity import (
    Permission,
    Role,
    RolePermission,
    UserPermission,
)
from app.internal.permission.repository import PermissionRepository
from app.internal.user.entity import User, UserCompanyAccess


class PermissionRepositoryImpl(PermissionRepository):
    """SQLModel implementation of permission repository."""

    def __init__(self, session: Session, current_user: User):
        """Initialize repository with database session and current user.

        Args:
            session: SQLModel database session
            current_user: Current authenticated user
        """
        self.db = session
        self.current_user = current_user

    # ===================================================================
    # Permission Methods
    # ===================================================================

    def create_permission(
        self,
        code: str,
        description: str | None = None,
        module_name: str | None = None,
    ) -> Permission:
        """Create a new permission."""
        permission = Permission(
            code=code,
            description=description,
            module_name=module_name,
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_by_code(self, code: str) -> Permission | None:
        """Get permission by code."""
        statement = select(Permission).where(Permission.code == code)
        return self.db.exec(statement).first()

    def get_permission_by_id(self, permission_id: UUID) -> Permission | None:
        """Get permission by ID."""
        return self.db.get(Permission, permission_id)

    def get_all_permissions(
        self,
        module_name: str | None = None,
    ) -> list[Permission]:
        """Get all permissions, optionally filtered by module."""
        statement = select(Permission)

        if module_name:
            statement = statement.where(Permission.module_name == module_name)

        return list(self.db.exec(statement).all())

    # ===================================================================
    # Role Methods
    # ===================================================================

    def create_role(
        self,
        name: str,
        description: str | None = None,
        is_system: bool = False,
    ) -> Role:
        """Create a new role."""
        role = Role(
            name=name,
            description=description,
            is_system=is_system,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        statement = select(Role).where(Role.name == name)
        return self.db.exec(statement).first()

    def get_role_by_id(self, role_id: UUID) -> Role | None:
        """Get role by ID."""
        return self.db.get(Role, role_id)

    def get_all_roles(self) -> list[Role]:
        """Get all roles."""
        statement = select(Role)
        return list(self.db.exec(statement).all())

    def update_role(
        self,
        role_id: UUID,
        description: str | None = None,
    ) -> Role:
        """Update a role."""
        role = self.db.get(Role, role_id)
        if role and description is not None:
            role.description = description
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        return role  # type: ignore

    def delete_role(self, role_id: UUID) -> None:
        """Delete a role."""
        role = self.db.get(Role, role_id)
        if role:
            self.db.delete(role)
            self.db.commit()

    # ===================================================================
    # Role-Permission Assignment Methods
    # ===================================================================

    def has_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Check if role has a permission."""
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        return self.db.exec(statement).first() is not None

    def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Assign a permission to a role."""
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.db.add(role_permission)
        self.db.commit()

    def remove_permission_from_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Remove a permission from a role."""
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        role_permission = self.db.exec(statement).first()
        if role_permission:
            self.db.delete(role_permission)
            self.db.commit()

    def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """Get all permissions for a role."""
        statement = (
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        return list(self.db.exec(statement).all())

    # ===================================================================
    # User Permission Methods
    # ===================================================================

    def get_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
    ) -> UserPermission | None:
        """Get a user's direct permission assignment."""
        statement = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
        )
        return self.db.exec(statement).first()

    def get_user_permission_by_code(
        self,
        user_id: UUID,
        permission_code: str,
    ) -> UserPermission | None:
        """Get a user's direct permission by code."""
        statement = (
            select(UserPermission)
            .join(Permission)
            .where(
                UserPermission.user_id == user_id,
                Permission.code == permission_code,
            )
        )
        return self.db.exec(statement).first()

    def grant_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
        granted: bool = True,
    ) -> None:
        """Grant or revoke a direct permission to/from a user."""
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            granted=granted,
        )
        self.db.add(user_permission)
        self.db.commit()

    def update_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
        granted: bool,
    ) -> None:
        """Update an existing user permission."""
        user_permission = self.get_user_permission(user_id, permission_id)
        if user_permission:
            user_permission.granted = granted
            self.db.add(user_permission)
            self.db.commit()

    def check_user_has_permission_via_role(  # type: ignore[misc]
        self,
        user_id: UUID,
        permission_code: str,
    ) -> bool:
        """Check if user has permission via their role assignments."""
        # Query:
        # 1. Get all companies user has access to
        # 2. Get all roles assigned to user via UserCompanyAccess
        # 3. Check if any of those roles have the permission
        statement = (
            select(Permission)
            .join(RolePermission)
            .join(Role)
            .join(UserCompanyAccess, UserCompanyAccess.role_id == Role.id)  # type: ignore[arg-type]
            .where(
                UserCompanyAccess.user_id == user_id,
                Permission.code == permission_code,
            )
        )
        return self.db.exec(statement).first() is not None
