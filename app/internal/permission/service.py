"""Business logic for Permission and Role management."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.permission.entity import Permission, Role
from app.internal.permission.repository_impl import PermissionRepositoryImpl
from app.internal.user.entity import User


class PermissionService:
    """Service layer for permission and role management."""

    def __init__(self, session: Session, current_user: User):
        """Initialize service with database session and current user.

        Args:
            session: SQLModel database session
            current_user: Current authenticated user
        """
        self.repository = PermissionRepositoryImpl(session, current_user)
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
        """Create a new permission.

        Args:
            code: Permission code (e.g., "product:create")
            description: Optional description
            module_name: Optional module name (e.g., "inventory")

        Returns:
            Created permission

        Raises:
            HTTPException: 409 if permission code already exists
        """
        # Check if permission code already exists
        existing = self.repository.get_by_code(code=code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission with code '{code}' already exists",
            )

        return self.repository.create_permission(
            code=code,
            description=description,
            module_name=module_name,
        )

    def list_all_permissions(
        self,
        module_name: str | None = None,
    ) -> list[Permission]:
        """List all permissions, optionally filtered by module.

        Args:
            module_name: Optional module name filter

        Returns:
            List of permissions
        """
        return self.repository.get_all_permissions(module_name=module_name)

    def get_permission_by_code(self, code: str) -> Permission:
        """Get permission by code.

        Args:
            code: Permission code

        Returns:
            Permission

        Raises:
            HTTPException: 404 if permission not found
        """
        permission = self.repository.get_by_code(code=code)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with code '{code}' not found",
            )
        return permission

    # ===================================================================
    # Role Methods
    # ===================================================================

    def create_role(
        self,
        name: str,
        description: str | None = None,
        is_system: bool = False,
    ) -> Role:
        """Create a new role.

        Args:
            name: Role name (unique)
            description: Optional description
            is_system: Whether this is a system role (cannot be deleted)

        Returns:
            Created role

        Raises:
            HTTPException: 409 if role name already exists
        """
        # Check if role name already exists
        existing = self.repository.get_role_by_name(name=name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role with name '{name}' already exists",
            )

        return self.repository.create_role(
            name=name,
            description=description,
            is_system=is_system,
        )

    def update_role(
        self,
        role_id: UUID,
        description: str | None = None,
    ) -> Role:
        """Update a role.

        Args:
            role_id: Role ID
            description: New description

        Returns:
            Updated role

        Raises:
            HTTPException: 404 if role not found
        """
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )

        return self.repository.update_role(
            role_id=role_id,
            description=description,
        )

    def delete_role(self, role_id: UUID) -> None:
        """Delete a role.

        Args:
            role_id: Role ID

        Raises:
            HTTPException: 404 if role not found, 403 if system role
        """
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )

        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system role",
            )

        self.repository.delete_role(role_id=role_id)

    def list_all_roles(self) -> list[Role]:
        """List all roles.

        Returns:
            List of roles
        """
        return self.repository.get_all_roles()

    # ===================================================================
    # Role-Permission Assignment Methods
    # ===================================================================

    def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Assign a permission to a role.

        Args:
            role_id: Role ID
            permission_id: Permission ID

        Raises:
            HTTPException: 404 if role/permission not found, 409 if already assigned
        """
        # Verify role exists
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )

        # Verify permission exists
        permission = self.repository.get_permission_by_id(
            permission_id=permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )

        # Check if already assigned
        if self.repository.has_permission(
            role_id=role_id, permission_id=permission_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already assigned to role",
            )

        self.repository.assign_permission_to_role(
            role_id=role_id,
            permission_id=permission_id,
        )

    def remove_permission_from_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Remove a permission from a role.

        Args:
            role_id: Role ID
            permission_id: Permission ID

        Raises:
            HTTPException: 404 if role/permission not found
        """
        # Verify role exists
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )

        # Verify permission exists
        permission = self.repository.get_permission_by_id(
            permission_id=permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )

        # Check if assigned
        if not self.repository.has_permission(
            role_id=role_id, permission_id=permission_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not assigned to role",
            )

        self.repository.remove_permission_from_role(
            role_id=role_id,
            permission_id=permission_id,
        )

    def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """Get all permissions for a role.

        Args:
            role_id: Role ID

        Returns:
            List of permissions

        Raises:
            HTTPException: 404 if role not found
        """
        # Verify role exists
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )

        return self.repository.get_role_permissions(role_id=role_id)

    # ===================================================================
    # User Permission Methods
    # ===================================================================

    def grant_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Grant a direct permission to a user.

        Args:
            user_id: User ID
            permission_id: Permission ID

        Raises:
            HTTPException: 404 if permission not found
        """
        # Verify permission exists
        permission = self.repository.get_permission_by_id(
            permission_id=permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )

        # Check if user already has a direct permission (grant or revoke)
        existing = self.repository.get_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        if existing:
            # Update existing permission
            self.repository.update_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=True,
            )
        else:
            # Create new permission grant
            self.repository.grant_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=True,
            )

    def revoke_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Revoke a direct permission from a user.

        Args:
            user_id: User ID
            permission_id: Permission ID

        Raises:
            HTTPException: 404 if permission not found
        """
        # Verify permission exists
        permission = self.repository.get_permission_by_id(
            permission_id=permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )

        # Check if user already has a direct permission
        existing = self.repository.get_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        if existing:
            # Update existing permission to revoke
            self.repository.update_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=False,
            )
        else:
            # Create new permission revoke
            self.repository.grant_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=False,
            )

    def check_user_has_permission(
        self,
        user_id: UUID,
        permission_code: str,
    ) -> bool:
        """Check if user has a permission.

        Priority:
        1. Direct UserPermission (grant or revoke)
        2. Role permissions via UserCompanyAccess

        Args:
            user_id: User ID
            permission_code: Permission code (e.g., "product:create")

        Returns:
            True if user has permission, False otherwise
        """
        # Check for direct user permission (highest priority)
        user_perm = self.repository.get_user_permission_by_code(
            user_id=user_id,
            permission_code=permission_code,
        )

        if user_perm:
            # Direct permission exists - return granted status
            return user_perm.granted

        # Check via role assignments
        return self.repository.check_user_has_permission_via_role(
            user_id=user_id,
            permission_code=permission_code,
        )
