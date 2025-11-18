from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import verify_token
from app.domain.entities.company import (
    CompaniesResponse,
    CompanyCreate,
    CompanyResponse,
)
from app.infrastructure.database import get_session
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/company",
    tags=["Companies"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)

service = CompanyService()


@router.post("/", response_model=CompanyResponse)
def create_company(company: CompanyCreate):
    """
    Create a new company

    Returns the created company
    """

    try:
        return service.create_company(company=company)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/", response_model=CompaniesResponse)
def list_companies():
    """
    Get all companies.

    Returns a list of all companies.
    """

    try:
        return service.list_all_companies()
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
