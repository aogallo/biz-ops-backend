from abc import ABC, abstractmethod

from app.domain.entities.company import Company, CompanyCreate


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
    def get_by_id(self, id: int) -> Company | None:
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
