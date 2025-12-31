from abc import ABC, abstractmethod
from uuid import UUID

from app.internal.company.entity import Company, CompanyCreate


class CompanyRepository(ABC):
    """
    Company repository
    """

    @abstractmethod
    def create(self, company: CompanyCreate) -> Company:
        """
        Create a company
        """
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Company | None:
        """
        Get a company by id
        """
        pass

    @abstractmethod
    def get_all_companies(self) -> list[Company]:
        """
        Get all companies
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Company | None:
        """
        Get a company by email
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Company | None:
        """
        Get company by name
        """
        pass
