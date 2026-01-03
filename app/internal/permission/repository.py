"""Abstract repository interface for Permission and Role entities."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.internal.permission.entity import Permission, Role, UserPermission


class PermissionRepository(ABC):
    """Abstract base class for permission repository operations."""

    # ===================================================================
    # Permission Methods
    # ===================================================================

    @abstractmethod
    def create_permission(
        self,
        code: str,
        description: str | None = None,
        module_name: str | None = None,
    ) -> Permission:
        """Create a new permission."""
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Permission | None:
        """Get permission by code."""
        pass

    @abstractmethod
    def get_permission_by_id(self, permission_id: UUID) -> Permission | None:
        """Get permission by ID."""
        pass

    @abstractmethod
    def get_all_permissions(
        self,
        module_name: str | None = None,
    ) -> list[Permission]:
        """Get all permissions, optionally filtered by module."""
        pass

    # ===================================================================
    # Role Methods
    # ===================================================================

    @abstractmethod
    def create_role(
        self,
        name: str,
        description: str | None = None,
        is_system: bool = False,
    ) -> Role:
        """Create a new role."""
        pass

    @abstractmethod
    def get_role_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: UUID) -> Role | None:
        """Get role by ID."""
        pass

    @abstractmethod
    def get_all_roles(self) -> list[Role]:
        """Get all roles."""
        pass

    @abstractmethod
    def update_role(
        self,
        role_id: UUID,
        description: str | None = None,
    ) -> Role:
        """Update a role."""
        pass

    @abstractmethod
    def delete_role(self, role_id: UUID) -> None:
        """Delete a role."""
        pass

    # ===================================================================
    # Role-Permission Assignment Methods
    # ===================================================================

    @abstractmethod
    def has_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Check if role has a permission."""
        pass

    @abstractmethod
    def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Assign a permission to a role."""
        pass

    @abstractmethod
    def remove_permission_from_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        """Remove a permission from a role."""
        pass

    @abstractmethod
    def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """Get all permissions for a role."""
        pass

    # ===================================================================
    # User Permission Methods
    # ===================================================================

    @abstractmethod
    def get_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
    ) -> UserPermission | None:
        """Get a user's direct permission assignment."""
        pass

    @abstractmethod
    def get_user_permission_by_code(
        self,
        user_id: UUID,
        permission_code: str,
    ) -> UserPermission | None:
        """Get a user's direct permission by code."""
        pass

    @abstractmethod
    def grant_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
        granted: bool = True,
    ) -> None:
        """Grant or revoke a direct permission to/from a user."""
        pass

    @abstractmethod
    def update_user_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
        granted: bool,
    ) -> None:
        """Update an existing user permission."""
        pass

    @abstractmethod
    def check_user_has_permission_via_role(
        self,
        user_id: UUID,
        permission_code: str,
    ) -> bool:
        """Check if user has permission via their role assignments."""
        pass
