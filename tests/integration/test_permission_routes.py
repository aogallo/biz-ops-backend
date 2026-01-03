"""Integration tests for permission API routes."""

from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.internal.permission.entity import Permission, Role, RolePermission
from app.internal.user.entity import User


class TestPermissionRoutes:
    """Test permission management routes."""

    def test_create_permission_success(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test creating a new permission."""
        permission_data = {
            "code": "invoice:create",
            "description": "Create invoices",
            "moduleName": "accounting",
        }

        response = authenticated_client.post(
            "/api/v1/permissions", json=permission_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "invoice:create"
        assert data["description"] == "Create invoices"
        assert data["moduleName"] == "accounting"
        assert "id" in data

    def test_create_permission_duplicate_code(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test creating a permission with duplicate code fails."""
        # Create first permission
        perm = Permission(
            code="product:create",
            description="Create products",
            module_name="inventory",
        )
        session.add(perm)
        session.commit()

        # Attempt to create duplicate
        permission_data = {
            "code": "product:create",
            "description": "Duplicate",
            "moduleName": "inventory",
        }

        response = authenticated_client.post(
            "/api/v1/permissions", json=permission_data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_list_permissions(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test listing all permissions."""
        # Create test permissions
        perms = [
            Permission(
                code="product:read",
                description="Read products",
                module_name="inventory",
            ),
            Permission(
                code="product:create",
                description="Create products",
                module_name="inventory",
            ),
        ]
        for perm in perms:
            session.add(perm)
        session.commit()

        response = authenticated_client.get("/api/v1/permissions")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["permissions"]) >= 2
        codes = [p["code"] for p in data["permissions"]]
        assert "product:read" in codes
        assert "product:create" in codes

    def test_get_permission_by_id(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting a single permission by ID."""
        perm = Permission(
            code="invoice:read",
            description="Read invoices",
            module_name="accounting",
        )
        session.add(perm)
        session.commit()
        session.refresh(perm)

        response = authenticated_client.get(f"/api/v1/permissions/{perm.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(perm.id)
        assert data["code"] == "invoice:read"

    def test_get_permission_not_found(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting a non-existent permission returns 404."""
        fake_id = uuid4()
        response = authenticated_client.get(f"/api/v1/permissions/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRoleRoutes:
    """Test role management routes."""

    def test_create_role_success(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test creating a new role."""
        role_data = {
            "name": "accountant",
            "description": "Accounting role",
            "isSystem": False,
        }

        response = authenticated_client.post("/api/v1/roles", json=role_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "accountant"
        assert data["description"] == "Accounting role"
        assert data["isSystem"] is False
        assert "id" in data

    def test_create_role_duplicate_name(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test creating a role with duplicate name fails."""
        # Create first role
        role = Role(name="admin", description="Administrator", is_system=True)
        session.add(role)
        session.commit()

        # Attempt to create duplicate
        role_data = {
            "name": "admin",
            "description": "Duplicate admin",
            "isSystem": False,
        }

        response = authenticated_client.post("/api/v1/roles", json=role_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_list_roles(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test listing all roles."""
        # Create test roles
        roles = [
            Role(name="viewer", description="View only", is_system=False),
            Role(name="editor", description="Can edit", is_system=False),
        ]
        for role in roles:
            session.add(role)
        session.commit()

        response = authenticated_client.get("/api/v1/roles")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["roles"]) >= 2
        names = [r["name"] for r in data["roles"]]
        assert "viewer" in names
        assert "editor" in names

    def test_get_role_by_id(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting a single role by ID."""
        role = Role(
            name="manager", description="Manager role", is_system=False
        )
        session.add(role)
        session.commit()
        session.refresh(role)

        response = authenticated_client.get(f"/api/v1/roles/{role.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(role.id)
        assert data["name"] == "manager"

    def test_delete_role_success(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test deleting a non-system role."""
        role = Role(name="temp", description="Temporary role", is_system=False)
        session.add(role)
        session.commit()
        session.refresh(role)

        response = authenticated_client.delete(f"/api/v1/roles/{role.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify role is deleted
        deleted_role = session.get(Role, role.id)
        assert deleted_role is None

    def test_delete_system_role_forbidden(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test deleting a system role is forbidden."""
        role = Role(name="owner", description="System owner", is_system=True)
        session.add(role)
        session.commit()
        session.refresh(role)

        response = authenticated_client.delete(f"/api/v1/roles/{role.id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "system role" in response.json()["detail"].lower()


class TestRolePermissionRoutes:
    """Test role-permission assignment routes."""

    def test_assign_permission_to_role_success(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test assigning a permission to a role."""
        # Create role and permission
        role = Role(
            name="accountant", description="Accountant", is_system=False
        )
        perm = Permission(
            code="invoice:read",
            description="Read invoices",
            module_name="accounting",
        )
        session.add(role)
        session.add(perm)
        session.commit()
        session.refresh(role)
        session.refresh(perm)

        # Assign permission to role
        response = authenticated_client.post(
            f"/api/v1/roles/{role.id}/permissions/{perm.id}"
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["roleId"] == str(role.id)
        assert data["permissionId"] == str(perm.id)

    def test_assign_permission_to_role_duplicate(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test assigning the same permission twice returns 400."""
        # Create role, permission, and existing assignment
        role = Role(name="editor", description="Editor", is_system=False)
        perm = Permission(
            code="product:update",
            description="Update products",
            module_name="inventory",
        )
        session.add(role)
        session.add(perm)
        session.commit()
        session.refresh(role)
        session.refresh(perm)

        # Create existing assignment
        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
        session.add(role_perm)
        session.commit()

        # Attempt duplicate assignment
        response = authenticated_client.post(
            f"/api/v1/roles/{role.id}/permissions/{perm.id}"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already assigned" in response.json()["detail"]

    def test_remove_permission_from_role_success(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test removing a permission from a role."""
        # Create role, permission, and assignment
        role = Role(name="editor", description="Editor", is_system=False)
        perm = Permission(
            code="product:delete",
            description="Delete products",
            module_name="inventory",
        )
        session.add(role)
        session.add(perm)
        session.commit()
        session.refresh(role)
        session.refresh(perm)

        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
        session.add(role_perm)
        session.commit()

        # Remove permission from role
        response = authenticated_client.delete(
            f"/api/v1/roles/{role.id}/permissions/{perm.id}"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_get_role_permissions(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting all permissions for a role."""
        # Create role and permissions
        role = Role(
            name="accountant", description="Accountant", is_system=False
        )
        perm1 = Permission(
            code="invoice:read",
            description="Read invoices",
            module_name="accounting",
        )
        perm2 = Permission(
            code="invoice:create",
            description="Create invoices",
            module_name="accounting",
        )
        session.add(role)
        session.add(perm1)
        session.add(perm2)
        session.commit()
        session.refresh(role)
        session.refresh(perm1)
        session.refresh(perm2)

        # Assign permissions to role
        session.add(RolePermission(role_id=role.id, permission_id=perm1.id))
        session.add(RolePermission(role_id=role.id, permission_id=perm2.id))
        session.commit()

        # Get role permissions
        response = authenticated_client.get(
            f"/api/v1/roles/{role.id}/permissions"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["permissions"]) == 2
        codes = [p["code"] for p in data["permissions"]]
        assert "invoice:read" in codes
        assert "invoice:create" in codes


class TestUserPermissionRoutes:
    """Test user-permission assignment routes (direct permissions)."""

    def test_grant_direct_permission_to_user(
        self,
        authenticated_client: TestClient,
        session: Session,
        test_user: User,
    ):
        """Test granting a direct permission to a user."""
        # Create permission
        perm = Permission(
            code="report:export",
            description="Export reports",
            module_name="accounting",
        )
        session.add(perm)
        session.commit()
        session.refresh(perm)

        # Grant permission to user
        payload = {"permissionId": str(perm.id), "granted": True}
        response = authenticated_client.post(
            f"/api/v1/users/{test_user.id}/permissions", json=payload
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["userId"] == str(test_user.id)
        assert data["permissionId"] == str(perm.id)
        assert data["granted"] is True

    def test_revoke_direct_permission_from_user(
        self,
        authenticated_client: TestClient,
        session: Session,
        test_user: User,
    ):
        """Test revoking a direct permission from a user."""
        # Create permission
        perm = Permission(
            code="product:delete",
            description="Delete products",
            module_name="inventory",
        )
        session.add(perm)
        session.commit()
        session.refresh(perm)

        # Revoke permission from user
        payload = {"permissionId": str(perm.id), "granted": False}
        response = authenticated_client.post(
            f"/api/v1/users/{test_user.id}/permissions", json=payload
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["userId"] == str(test_user.id)
        assert data["permissionId"] == str(perm.id)
        assert data["granted"] is False

    def test_get_user_effective_permissions(
        self,
        authenticated_client: TestClient,
        session: Session,
        test_user: User,
    ):
        """Test getting user's effective permissions (from roles + direct)."""
        response = authenticated_client.get(
            f"/api/v1/users/{test_user.id}/permissions"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], list)
