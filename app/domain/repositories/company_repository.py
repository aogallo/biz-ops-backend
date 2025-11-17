from abc import ABC, abstractmethod

from app.domain.entities.company import Company, CompanyCreate


class CompanyRepository(ABC):
    @abstractmethod
    def create(self, company: CompanyCreate) -> Company:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Company | None:
        pass

    @abstractmethod
    def get_all_companies(self) -> list[Company]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Company | None:
        pass
