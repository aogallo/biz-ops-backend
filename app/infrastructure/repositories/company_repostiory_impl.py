from sqlmodel import Session, or_, select

from app.domain.entities.company import Company, CompanyCreate
from app.domain.repositories.company_repository import CompanyRepository
from app.infrastructure.database import get_current_session


class CompanyRepositoryImpl(CompanyRepository):
    """Implementation of Company Repository Interface."""

    def __init__(self, session: Session | None = None) -> None:
        self.db = session or get_current_session()

    def create(self, company: CompanyCreate) -> Company:
        """Create a new company"""
        company_created = Company.model_validate(company)
        self.db.add(company_created)
        self.db.commit()
        self.db.refresh(company_created)
        print("company created", company_created)
        return company_created

    def get_by_id(self, id: int) -> Company | None:
        """Get company by ID"""
        return self.db.get(Company, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Company]:
        """Get all companys with pagination"""
        statement = select(Company).offset(skip).limit(limit)
        result = self.db.exec(statement)
        return list(result)

    def update(self, id: int, model: Company) -> Company:
        """Update an existing company"""
        db_company = self.db.get(Company, id)
        if not db_company:
            raise ValueError(f"company with id {id} not found")

        company_data = model.model_dump(exclude_unset=True)
        for field, value in company_data.items():
            setattr(db_company, field, value)

        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company

    def delete(self, id: int) -> bool:
        """Delete a company by ID"""
        company = self.db.get(Company, id)
        if not company:
            return False

        self.db.delete(company)
        self.db.commit()
        return True

    def exists(self, id: int) -> bool:
        """Check if company exists by ID"""
        company = self.db.get(Company, id)
        return company is not None

    def get_all_companies(self) -> list[Company]:
        """Get all companys (alias for get_all)"""
        return self.get_all()

    def get_by_email(self, email: str) -> Company | None:
        """Get company by email"""
        statement = select(Company).where(Company.email == email)
        result = self.db.exec(statement)
        return result.first()

    def get_company_by_nit(self, nit: str) -> Company | None:
        """Get company by NIT"""
        statement = select(Company).where(Company.nit == nit)
        result = self.db.exec(statement)
        return result.first()

    def search_companies(self, search_term: str) -> list[Company]:
        """Search companys by name or NIT"""
        statement = select(Company).where(
            or_(Company.name == search_term, Company.nit == f"%{search_term}%")
        )
        result = self.db.exec(statement)
        return list(result)
