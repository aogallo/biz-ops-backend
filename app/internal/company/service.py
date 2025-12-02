from fastapi import HTTPException, status
from sqlmodel import Session

from app.domain.entities.user import User
from app.internal.company.entity import CompanyCreate
from app.internal.company.repostiory_impl import CompanyRepositoryImpl


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

    def list_all_companies(self):
        count = self.repository.get_count()
        companies = self.repository.get_all()
        return {"count": count, "data": companies}
