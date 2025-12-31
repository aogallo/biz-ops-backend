from abc import ABC, abstractmethod

from app.internal.organization.entity import Organization


class OrganizationRepository(ABC):
    """Organization repository interface"""

    @abstractmethod
    def create(self, organization: Organization) -> Organization:
        pass

    @abstractmethod
    def get_by_id(self, organization_id: int) -> Organization | None:
        """Get a organization by id"""
        pass

    @abstractmethod
    def delete(self, organization: Organization) -> bool:
        """Delete a organization by id"""
        pass

    @abstractmethod
    def get_all(self, offset: int = 0, limit: int = 100) -> list[Organization]:
        """Get all organizations (scoped to company)"""
        pass
