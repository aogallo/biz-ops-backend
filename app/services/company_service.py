from fastapi import HTTPException, status

from app.domain.entities.company import CompanyCreate
from app.infrastructure.repositories.company_repostiory_impl import (
    CompanyRepositoryImpl,
)


class CompanyService:
    """Service for managing companies."""

    def __init__(self) -> None:
        self.repository = CompanyRepositoryImpl()

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
