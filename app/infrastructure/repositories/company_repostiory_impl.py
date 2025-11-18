from typing import Any

from sqlmodel import Session, func, or_, select

from app.domain.entities.company import Company, CompanyCreate
from app.domain.repositories.company_repository import CompanyRepository
from app.infrastructure.database import get_current_session


class CompanyRepositoryImpl(CompanyRepository):
    """Implementation of Company Repository"""

    def __init__(self, session: Session | None = None) -> None:
        self.db = session or get_current_session()

    def create(self, company: CompanyCreate) -> Company:
        """Create a new company"""
        company_created: Company = Company.model_validate(company)
        self.db.add(company_created)
        self.db.commit()
        self.db.refresh(company_created)
        return company_created

    def get_by_id(self, id: int) -> Company | None:
        """Get company by ID"""
        company: Company | None = self.db.get(Company, id)
        return company

    def get_count(self) -> int:
        """Get count of companies"""
        count_statement = select(func.count()).select_from(Company)
        count: int = self.db.exec(count_statement).one()
        return count

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Company]:
        """Get all companies"""
        statement = select(Company).offset(skip).limit(limit)
        result: list[Company] = list(self.db.exec(statement))
        return list(result)

    def update(self, id: int, model: Company) -> Company:
        """Update a company by id"""
        db_company: Company | None = self.db.get(Company, id)
        if db_company is None:
            raise ValueError(f"company with id {id} not found")

        company_data: dict[str, Any] = model.model_dump(exclude_unset=True)

        for field, value in company_data.items():
            setattr(db_company, field, value)

        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company

    def delete(self, id: int) -> bool:
        """Delete a company by id"""
        company: Company | None = self.db.get(Company, id)
        if company is None:
            return False

        self.db.delete(company)
        self.db.commit()
        self.db.refresh(company)
        return True

    def exists(self, id: int) -> bool:
        """Check if company exists by id"""
        company: Company | None = self.db.get(Company, id)
        return company is not None

    def get_all_companies(self) -> list[Company]:
        """Get all companies"""
        companies: list[Company] = self.get_all()
        return companies

    def get_by_email(self, email: str) -> Company | None:
        """Get a company by email"""
        statement = select(Company).where(Company.email == email)
        result: Company | None = self.db.exec(statement).one_or_none()
        return result

    def get_company_by_nit(self, nit: str) -> Company | None:
        """Get a company by NIT"""
        statement = select(Company).where(Company.nit == nit)
        result: Company | None = self.db.exec(statement).one_or_none()
        return result

    def search_companies(self, search_term: str) -> list[Company]:
        """Search companies by name or NIT"""
        statement = select(Company).where(
            or_(Company.name == search_term, Company.nit == f"%{search_term}%")
        )
        result: list[Company] = list(self.db.exec(statement))
        return result
