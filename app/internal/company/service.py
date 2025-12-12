from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.company.entity import Company, CompanyCreate
from app.internal.company.repostiory_impl import CompanyRepositoryImpl
from app.internal.user.entity import User


class CompanyService:
    """Service for managing companies."""

    def __init__(self, session: Session, current_user: User) -> None:
        self.repository = CompanyRepositoryImpl(session, current_user)

    def create_company(self, company: CompanyCreate):
        existed_company = self.repository.get_company_by_nit(nit=company.nit)

        if existed_company is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company already exists",
            )

        return self.repository.create(company=company)

    def update_company(self, company_id: int, company_update: Company):
        """Update a company by ID."""
        existing_company = self.repository.get_by_id(company_id)

        if existing_company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        return self.repository.update(id=company_id, model=company_update)

    def list_all_companies(
        self,
        offset: int,
        limit: int,
        managed_by_accountant: bool | None = None,
    ):
        """List all companies, optionally filtered by managed_by_accountant."""
        if managed_by_accountant is not None:
            companies = self.repository.get_by_managed_status(
                managed_by_accountant=managed_by_accountant,
                offset=offset,
                limit=limit,
            )
            count = len(companies)
        else:
            count = self.repository.get_count()
            companies = self.repository.get_all(offset, limit)

        return {"count": count, "data": companies}

    def get_by_id(self, id: int):
        """Get company by id"""
        existing_company = self.repository.get_by_id(id)
        if existing_company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        return existing_company
