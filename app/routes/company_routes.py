from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.dependencies import get_current_user, verify_token
from app.domain.entities.company import CompanyCreate as CompanyCreateEntity
from app.infrastructure.database import get_session
from app.schemas.company_schema import (
    CompaniesResponse,
    CompanyCreate,
    CompanyResponse,
)
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.post("", response_model=CompanyResponse)
def create_company(
    company: CompanyCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Create a new company

    Returns the created company
    """

    try:
        service = CompanyService(session, current_user)
        # Convert schema to entity
        company_entity = CompanyCreateEntity(**company.model_dump())
        created_company = service.create_company(company=company_entity)
        return CompanyResponse.model_validate(created_company)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("", response_model=CompaniesResponse)
def list_companies(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Get all companies.

    Returns a list of all companies.
    """

    try:
        service = CompanyService(session, current_user)
        result = service.list_all_companies()
        return CompaniesResponse(
            count=result["count"],
            data=[CompanyResponse.model_validate(c) for c in result["data"]],
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
