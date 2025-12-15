from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.company.entity import Company
from app.internal.company.entity import CompanyCreate as CompanyCreateEntity
from app.internal.company.schema import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.internal.company.service import CompanyService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.post(
    "", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED
)
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
        raise e


@router.get("", response_model=CompanyListResponse)
def list_companies(
    page: int = 1,
    limit: int = 10,
    managed_by_accountant: bool | None = None,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all companies with pagination and optional filtering."""
    try:
        offset = calculate_offset(page=page, page_size=limit)

        service = CompanyService(session, current_user)
        result = service.list_all_companies(
            managed_by_accountant=managed_by_accountant,
            offset=offset,
            limit=limit,
        )

        pagination = PaginationResponse(
            total=result.count,
            page_size=limit,
            page_index=page - 1,
        )

        # Convert entities to response schemas
        companies_response = [
            CompanyResponse.model_validate(company)
            for company in result.companies
        ]

        return CompanyListResponse(
            companies=companies_response, pagination=pagination
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company: CompanyUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Update a company by ID.

    Returns the updated company.
    """

    try:
        service = CompanyService(session, current_user)
        # Convert schema to entity
        company_entity = Company(**company.model_dump(exclude_unset=True))
        updated_company = service.update_company(
            company_id=company_id, company_update=company_entity
        )
        return CompanyResponse.model_validate(updated_company)
    except HTTPException as e:
        raise e


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(
    company_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Get a company by ID.

    Returns a company
    """
    try:
        service = CompanyService(session, current_user)
        existing_company = service.get_by_id(id=company_id)
        print(existing_company)
        return CompanyResponse.model_validate(existing_company)
    except HTTPException as e:
        raise e
