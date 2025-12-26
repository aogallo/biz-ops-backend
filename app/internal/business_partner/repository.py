from abc import ABC, abstractmethod
from uuid import UUID

from app.internal.business_partner.entity import (
    BusinessPartner,
    BusinessPartnerCreate,
)


class BusinessPartnerRepository(ABC):
    """
    Business Partner repository (organization-scoped).
    """

    @abstractmethod
    def create(
        self, business_partner_create: BusinessPartnerCreate
    ) -> BusinessPartner:
        """
        Create a business partner
        """
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> BusinessPartner | None:
        """
        Get a business partner by id
        """
        pass

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> list[BusinessPartner]:
        """
        Get all business partners (scoped to organization)
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> BusinessPartner | None:
        """
        Get business partner by email
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> BusinessPartner | None:
        """
        Get business partner by name
        """
        pass

    @abstractmethod
    def get_by_nit(self, nit: str) -> BusinessPartner | None:
        """
        Get business partner by NIT (scoped to organization)
        """
        pass
