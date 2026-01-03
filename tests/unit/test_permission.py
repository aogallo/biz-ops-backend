"""Unit tests for Permission and Role services - testing business logic in isolation."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.internal.permission.entity import (
    Permission,
    Role,
    UserPermission,
)
from app.internal.user.entity import User


class TestPermissionService:
    """Test PermissionService business logic with mocked dependencies."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        mock = Mock(spec=User)
        mock.id = uuid4()
        mock.auth_id = "auth0|test123"
        mock.auth0_user_id = "auth0|test123"
        mock.organization_id = uuid4()
        mock.is_superuser = True
        mock.permissions = []
        return mock

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def mock_repository(self):
        """Create a mock permission repository."""
        return Mock()

    @pytest.fixture
    def service(
        self,
        mock_session,
        mock_user,
        mock_repository,
        monkeypatch,
    ):
        """Create a PermissionService with mocked repository."""
        # Import here to avoid circular imports in tests
        from app.internal.permission.service import PermissionService

        service = PermissionService(
            session=mock_session,
            current_user=mock_user,
        )
        # Replace the repository with our mock
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    # ===================================================================
    # Permission Tests
    # ===================================================================

    def test_create_permission_success(
        self,
        service,
        mock_repository,
    ):
        """Test successful permission creation when code doesn't exist."""
        # Arrange
        permission_data = {
            "code": "product:create",
            "description": "Create products",
            "module_name": "inventory",
        }
        expected_permission = Permission(
            id=uuid4(),
            code="product:create",
            description="Create products",
            module_name="inventory",
        )
        # Mock repository responses
        mock_repository.get_by_code.return_value = (
            None  # No existing permission
        )
        mock_repository.create_permission.return_value = expected_permission

        # Act
        result = service.create_permission(**permission_data)

        # Assert
        assert result == expected_permission
        assert result.code == "product:create"
        assert result.module_name == "inventory"
        mock_repository.get_by_code.assert_called_once_with(
            code="product:create"
        )
        mock_repository.create_permission.assert_called_once()

    def test_create_permission_duplicate_code(self, service, mock_repository):
        """Test that creating a permission with duplicate code raises 409 error."""
        # Arrange
        permission_data = {
            "code": "product:create",
            "description": "Create products",
            "module_name": "inventory",
        }
        existing_permission = Permission(
            id=uuid4(),
            code="product:create",
            description="Create products",
            module_name="inventory",
        )
        # Mock: Permission with same code already exists
        mock_repository.get_by_code.return_value = existing_permission

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_permission(**permission_data)

        # Verify error details
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()
        mock_repository.create_permission.assert_not_called()

    def test_list_all_permissions(self, service, mock_repository):
        """Test listing all permissions with optional module filter."""
        # Arrange
        expected_permissions = [
            Permission(
                id=uuid4(),
                code="product:create",
                description="Create products",
                module_name="inventory",
            ),
            Permission(
                id=uuid4(),
                code="product:read",
                description="Read products",
                module_name="inventory",
            ),
        ]
        mock_repository.get_all_permissions.return_value = expected_permissions

        # Act
        result = service.list_all_permissions(module_name="inventory")

        # Assert
        assert len(result) == 2
        assert result[0].code == "product:create"
        assert result[1].code == "product:read"
        mock_repository.get_all_permissions.assert_called_once_with(
            module_name="inventory"
        )

    def test_get_permission_by_code_success(self, service, mock_repository):
        """Test getting a permission by code when it exists."""
        # Arrange
        expected_permission = Permission(
            id=uuid4(),
            code="product:create",
            description="Create products",
            module_name="inventory",
        )
        mock_repository.get_by_code.return_value = expected_permission

        # Act
        result = service.get_permission_by_code(code="product:create")

        # Assert
        assert result == expected_permission
        mock_repository.get_by_code.assert_called_once_with(
            code="product:create"
        )

    def test_get_permission_by_code_not_found(self, service, mock_repository):
        """Test getting a permission by code when it doesn't exist."""
        # Arrange
        mock_repository.get_by_code.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_permission_by_code(code="nonexistent:permission")

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    # ===================================================================
    # Role Tests
    # ===================================================================

    def test_create_role_success(self, service, mock_repository):
        """Test successful role creation when name doesn't exist."""
        # Arrange
        role_data = {
            "name": "accountant",
            "description": "Accounting module access",
            "is_system": False,
        }
        expected_role = Role(
            id=uuid4(),
            name="accountant",
            description="Accounting module access",
            is_system=False,
        )
        mock_repository.get_role_by_name.return_value = None
        mock_repository.create_role.return_value = expected_role

        # Act
        result = service.create_role(**role_data)

        # Assert
        assert result == expected_role
        assert result.name == "accountant"
        mock_repository.get_role_by_name.assert_called_once_with(
            name="accountant"
        )
        mock_repository.create_role.assert_called_once()

    def test_create_role_duplicate_name(self, service, mock_repository):
        """Test that creating a role with duplicate name raises 409 error."""
        # Arrange
        role_data = {
            "name": "admin",
            "description": "Administrator",
            "is_system": True,
        }
        existing_role = Role(
            id=uuid4(),
            name="admin",
            description="Administrator",
            is_system=True,
        )
        mock_repository.get_role_by_name.return_value = existing_role

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_role(**role_data)

        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()

    def test_update_role_success(self, service, mock_repository):
        """Test successful role update."""
        # Arrange
        role_id = uuid4()
        update_data = {"description": "Updated description"}
        existing_role = Role(
            id=role_id,
            name="accountant",
            description="Old description",
            is_system=False,
        )
        updated_role = Role(
            id=role_id,
            name="accountant",
            description="Updated description",
            is_system=False,
        )
        mock_repository.get_role_by_id.return_value = existing_role
        mock_repository.update_role.return_value = updated_role

        # Act
        result = service.update_role(role_id=role_id, **update_data)

        # Assert
        assert result == updated_role
        assert result.description == "Updated description"
        mock_repository.get_role_by_id.assert_called_once_with(role_id=role_id)
        mock_repository.update_role.assert_called_once()

    def test_update_role_not_found(self, service, mock_repository):
        """Test updating a non-existent role."""
        # Arrange
        role_id = uuid4()
        mock_repository.get_role_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_role(role_id=role_id, description="New")

        assert exc_info.value.status_code == 404

    def test_delete_role_success(self, service, mock_repository):
        """Test successful role deletion when not a system role."""
        # Arrange
        role_id = uuid4()
        role = Role(
            id=role_id,
            name="custom_role",
            description="Custom role",
            is_system=False,
        )
        mock_repository.get_role_by_id.return_value = role
        mock_repository.delete_role.return_value = None

        # Act
        service.delete_role(role_id=role_id)

        # Assert
        mock_repository.get_role_by_id.assert_called_once_with(role_id=role_id)
        mock_repository.delete_role.assert_called_once_with(role_id=role_id)

    def test_delete_role_system_role_forbidden(self, service, mock_repository):
        """Test that deleting a system role raises 403 error."""
        # Arrange
        role_id = uuid4()
        system_role = Role(
            id=role_id,
            name="admin",
            description="System administrator",
            is_system=True,
        )
        mock_repository.get_role_by_id.return_value = system_role

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_role(role_id=role_id)

        assert exc_info.value.status_code == 403
        assert "system role" in str(exc_info.value.detail).lower()
        mock_repository.delete_role.assert_not_called()

    def test_list_all_roles(self, service, mock_repository):
        """Test listing all roles."""
        # Arrange
        expected_roles = [
            Role(
                id=uuid4(),
                name="admin",
                description="Administrator",
                is_system=True,
            ),
            Role(
                id=uuid4(),
                name="accountant",
                description="Accountant",
                is_system=False,
            ),
        ]
        mock_repository.get_all_roles.return_value = expected_roles

        # Act
        result = service.list_all_roles()

        # Assert
        assert len(result) == 2
        assert result[0].name == "admin"
        assert result[1].name == "accountant"

    # ===================================================================
    # Role-Permission Assignment Tests
    # ===================================================================

    def test_assign_permission_to_role_success(self, service, mock_repository):
        """Test assigning a permission to a role."""
        # Arrange
        role_id = uuid4()
        permission_id = uuid4()
        role = Role(id=role_id, name="accountant", is_system=False)
        permission = Permission(id=permission_id, code="account:read")

        mock_repository.get_role_by_id.return_value = role
        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.has_permission.return_value = False
        mock_repository.assign_permission_to_role.return_value = None

        # Act
        service.assign_permission_to_role(
            role_id=role_id,
            permission_id=permission_id,
        )

        # Assert
        mock_repository.assign_permission_to_role.assert_called_once_with(
            role_id=role_id,
            permission_id=permission_id,
        )

    def test_assign_permission_to_role_already_assigned(
        self,
        service,
        mock_repository,
    ):
        """Test assigning a permission that's already assigned."""
        # Arrange
        role_id = uuid4()
        permission_id = uuid4()
        role = Role(id=role_id, name="accountant", is_system=False)
        permission = Permission(id=permission_id, code="account:read")

        mock_repository.get_role_by_id.return_value = role
        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.has_permission.return_value = True  # Already assigned

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.assign_permission_to_role(
                role_id=role_id,
                permission_id=permission_id,
            )

        assert exc_info.value.status_code == 409
        mock_repository.assign_permission_to_role.assert_not_called()

    def test_remove_permission_from_role_success(
        self, service, mock_repository
    ):
        """Test removing a permission from a role."""
        # Arrange
        role_id = uuid4()
        permission_id = uuid4()
        role = Role(id=role_id, name="accountant", is_system=False)
        permission = Permission(id=permission_id, code="account:read")

        mock_repository.get_role_by_id.return_value = role
        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.has_permission.return_value = True
        mock_repository.remove_permission_from_role.return_value = None

        # Act
        service.remove_permission_from_role(
            role_id=role_id,
            permission_id=permission_id,
        )

        # Assert
        mock_repository.remove_permission_from_role.assert_called_once_with(
            role_id=role_id,
            permission_id=permission_id,
        )

    def test_get_role_permissions(self, service, mock_repository):
        """Test getting all permissions for a role."""
        # Arrange
        role_id = uuid4()
        expected_permissions = [
            Permission(id=uuid4(), code="account:read"),
            Permission(id=uuid4(), code="account:create"),
        ]
        mock_repository.get_role_by_id.return_value = Role(
            id=role_id,
            name="accountant",
        )
        mock_repository.get_role_permissions.return_value = (
            expected_permissions
        )

        # Act
        result = service.get_role_permissions(role_id=role_id)

        # Assert
        assert len(result) == 2
        assert result[0].code == "account:read"
        assert result[1].code == "account:create"

    # ===================================================================
    # User Permission Tests
    # ===================================================================

    def test_grant_user_permission_success(self, service, mock_repository):
        """Test granting a direct permission to a user."""
        # Arrange
        user_id = uuid4()
        permission_id = uuid4()
        permission = Permission(id=permission_id, code="product:delete")

        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.get_user_permission.return_value = (
            None  # No existing grant
        )
        mock_repository.grant_user_permission.return_value = None

        # Act
        service.grant_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        # Assert
        mock_repository.grant_user_permission.assert_called_once_with(
            user_id=user_id,
            permission_id=permission_id,
            granted=True,
        )

    def test_grant_user_permission_updates_existing(
        self, service, mock_repository
    ):
        """Test granting a permission updates existing revoke."""
        # Arrange
        user_id = uuid4()
        permission_id = uuid4()
        permission = Permission(id=permission_id, code="product:delete")
        existing_user_perm = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            granted=False,  # Currently revoked
        )

        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.get_user_permission.return_value = existing_user_perm
        mock_repository.update_user_permission.return_value = None

        # Act
        service.grant_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        # Assert
        mock_repository.update_user_permission.assert_called_once_with(
            user_id=user_id,
            permission_id=permission_id,
            granted=True,
        )

    def test_revoke_user_permission_success(self, service, mock_repository):
        """Test revoking a direct permission from a user."""
        # Arrange
        user_id = uuid4()
        permission_id = uuid4()
        permission = Permission(id=permission_id, code="product:delete")

        mock_repository.get_permission_by_id.return_value = permission
        mock_repository.get_user_permission.return_value = None
        mock_repository.grant_user_permission.return_value = None

        # Act
        service.revoke_user_permission(
            user_id=user_id,
            permission_id=permission_id,
        )

        # Assert
        mock_repository.grant_user_permission.assert_called_once_with(
            user_id=user_id,
            permission_id=permission_id,
            granted=False,  # Revoke
        )

    def test_check_user_has_permission_direct_grant(
        self, service, mock_repository
    ):
        """Test checking user permission with direct grant."""
        # Arrange
        user_id = uuid4()
        permission_code = "product:create"
        user_perm = UserPermission(
            user_id=user_id,
            permission_id=uuid4(),
            granted=True,
        )

        mock_repository.get_user_permission_by_code.return_value = user_perm

        # Act
        result = service.check_user_has_permission(
            user_id=user_id,
            permission_code=permission_code,
        )

        # Assert
        assert result is True

    def test_check_user_has_permission_direct_revoke(
        self, service, mock_repository
    ):
        """Test checking user permission with direct revoke."""
        # Arrange
        user_id = uuid4()
        permission_code = "product:create"
        user_perm = UserPermission(
            user_id=user_id,
            permission_id=uuid4(),
            granted=False,  # Explicitly revoked
        )

        mock_repository.get_user_permission_by_code.return_value = user_perm

        # Act
        result = service.check_user_has_permission(
            user_id=user_id,
            permission_code=permission_code,
        )

        # Assert
        assert result is False

    def test_check_user_has_permission_via_role(
        self, service, mock_repository
    ):
        """Test checking user permission via role assignment."""
        # Arrange
        user_id = uuid4()
        permission_code = "product:create"

        # No direct user permission
        mock_repository.get_user_permission_by_code.return_value = None
        # Has permission via role
        mock_repository.check_user_has_permission_via_role.return_value = True

        # Act
        result = service.check_user_has_permission(
            user_id=user_id,
            permission_code=permission_code,
        )

        # Assert
        assert result is True

    def test_check_user_has_permission_no_access(
        self, service, mock_repository
    ):
        """Test checking user permission when user has no access."""
        # Arrange
        user_id = uuid4()
        permission_code = "product:create"

        mock_repository.get_user_permission_by_code.return_value = None
        mock_repository.check_user_has_permission_via_role.return_value = False

        # Act
        result = service.check_user_has_permission(
            user_id=user_id,
            permission_code=permission_code,
        )

        # Assert
        assert result is False
