from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.internal.organization.entity import Organization
from app.internal.organization.schema import (
    OrganizationCreate,
    OrganizationUpdate,
)
from app.internal.organization.service import OrganizationService


class TestOrganizationService:
    """Test TestOrganization Service business logic"""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return Mock()

    @pytest.fixture
    def service(self, session, test_user, mock_repository, monkeypatch):
        """Create a OrganizationService with mocked repository."""
        service = OrganizationService(
            session=session,
            current_user=test_user,
        )
        # Replace the repository with our mock
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_list_organization_success(
        self,
        service,
        mock_repository,
    ):
        """Test successful organization list."""

        expected_result = [
            Organization(
                id=uuid4(),
                name="inventory",
                slug="inventory-test",
                created_by="test_user",
            ),
            Organization(
                id=uuid4(),
                name="accounting",
                slug="accounting-test",
                created_by="test_user",
            ),
        ]

        mock_repository.get_all.return_value = expected_result
        mock_repository.get_count.return_value = len(expected_result)

        result = service.get_organizations(offset=1, limit=5)

        assert result.count == 2
        assert result.organizations[0].name == "inventory"

    def test_create_duplicate_organization(
        self,
        service,
    ):
        """Test avoid creating duplicate organization"""
        organization_create = OrganizationCreate(
            name="organization test",
            slug="org-test",
            is_active=False,
        )

        org = Organization(**organization_create.model_dump())

        with pytest.raises(HTTPException) as exc_info:
            service.create_organization(org)

        # Verify error details
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()

    def test_create_organization(self, service, mock_repository):
        """Test create organization"""
        organization_create = OrganizationCreate(
            name="organization ake",
            slug="org-fa",
            is_active=False,
        )

        expected_organization = Organization(
            id=uuid4(),
            name="organization ake",
            slug="org-fa",
            is_active=False,
            created_by="userid",
        )

        org = Organization(**organization_create.model_dump())

        mock_repository.get_by_name.return_value = None
        mock_repository.create.return_value = expected_organization

        result = service.create_organization(org)

        assert result.name == "organization ake"
        assert not result.is_active

    def test_update_existing_organization(
        self,
        service,
        mock_repository,
    ):
        """Test update organization"""

        existing_org = Organization(
            id=uuid4(),
            name="organization ake",
            slug="org-fa",
            is_active=False,
            created_by="userid",
        )

        updated_payload = OrganizationUpdate(is_active=True, slug="open-door")

        mock_repository.get_by_id.return_value = existing_org
        mock_repository.update.return_value = existing_org

        result = service.update_organization_by_id(
            id="44444d",
            organization=updated_payload,
        )

        assert result.slug == "open-door"
