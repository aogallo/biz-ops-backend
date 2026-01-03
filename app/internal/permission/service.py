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
        permission_data,  # PermissionCreate schema
    ) -> Permission:
        """Create a new permission.

        Args:
            permission_data: PermissionCreate schema with permission details

        Returns:
            Created permission

        Raises:
            HTTPException: 409 if permission code already exists
        """
        # Check if permission code already exists
        existing = self.repository.get_by_code(code=permission_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission with code '{permission_data.code}' already exists",
            )

        return self.repository.create_permission(
            code=permission_data.code,
            description=permission_data.description,
            module_name=permission_data.module_name,
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

    def get_permission_by_id(self, permission_id: UUID) -> Permission:
        """Get permission by ID.

        Args:
            permission_id: Permission ID

        Returns:
            Permission

        Raises:
            HTTPException: 404 if permission not found
        """
        permission = self.repository.get_by_id(permission_id=permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )
        return permission

    # ===================================================================
    # Role Methods
    # ===================================================================

    def create_role(
        self,
        role_data,  # RoleCreate schema
    ) -> Role:
        """Create a new role.

        Args:
            role_data: RoleCreate schema with role details

        Returns:
            Created role

        Raises:
            HTTPException: 409 if role name already exists
        """
        # Check if role name already exists
        existing = self.repository.get_role_by_name(name=role_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists",
            )

        return self.repository.create_role(
            name=role_data.name,
            description=role_data.description,
            is_system=role_data.is_system,
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

    def get_role_by_id(self, role_id: UUID) -> Role:
        """Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role

        Raises:
            HTTPException: 404 if role not found
        """
        role = self.repository.get_role_by_id(role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID '{role_id}' not found",
            )
        return role

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
                status_code=status.HTTP_400_BAD_REQUEST,
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

    def assign_direct_permission_to_user(
        self,
        user_id: UUID,
        permission_id: UUID,
        granted: bool,
    ):
        """Assign a direct permission to a user (grant or revoke).

        Args:
            user_id: User ID
            permission_id: Permission ID
            granted: True to grant, False to revoke

        Returns:
            UserPermission assignment

        Raises:
            HTTPException: 404 if user or permission not found
        """
        from app.internal.permission.schema import (
            UserPermissionAssignmentResponse,
        )

        # Verify permission exists
        permission = self.repository.get_by_id(permission_id=permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID '{permission_id}' not found",
            )

        # Check if existing assignment
        existing = self.repository.get_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        if existing:
            # Update existing permission
            self.repository.update_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=granted,
            )
        else:
            # Create new permission assignment
            self.repository.grant_user_permission(
                user_id=user_id,
                permission_id=permission_id,
                granted=granted,
            )

        return UserPermissionAssignmentResponse(
            user_id=user_id,
            permission_id=permission_id,
            granted=granted,
        )

    def get_user_effective_permissions(
        self, user_id: UUID
    ) -> list[Permission]:
        """Get user's effective permissions (from roles + direct permissions).

        Returns the resolved set of permissions considering:
        1. Direct user permissions (grants and revokes)
        2. Role-based permissions via UserCompanyAccess

        Args:
            user_id: User ID

        Returns:
            List of effective permissions
        """
        # Get all permissions from user's roles
        role_permissions = self.repository.get_user_permissions_via_roles(
            user_id=user_id
        )

        # Get direct user permissions
        direct_permissions = self.repository.get_user_direct_permissions(
            user_id=user_id
        )

        # Build a set of permission IDs from roles
        effective_perm_ids = {perm.id for perm in role_permissions}

        # Apply direct permission grants and revokes
        for user_perm in direct_permissions:
            if user_perm.granted:
                # Grant adds permission to the set
                effective_perm_ids.add(user_perm.permission_id)
            else:
                # Revoke removes permission from the set
                effective_perm_ids.discard(user_perm.permission_id)

        # Return list of permission objects
        return [
            perm
            for perm in self.repository.get_all_permissions()
            if perm.id in effective_perm_ids
        ]
