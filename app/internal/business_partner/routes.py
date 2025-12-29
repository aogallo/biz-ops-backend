from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.business_partner.schema import (
    BusinessPartnerListResponse,
    BusinessPartnerResponse,
)
from app.internal.business_partner.service import BusinessPartnerService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

router = APIRouter(
    prefix="/customers",
    tags=["BusinessPartners"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.get("", response_model=BusinessPartnerListResponse)
def list_customers(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all customers with pagination."""
    offset = calculate_offset(page=page, page_size=limit)

    service = BusinessPartnerService(session, current_user)
    result = service.list_all_customers(offset=offset, limit=limit)

    pagination = PaginationResponse(
        total=result.count,
        page_index=page - 1,
        page_size=limit,
    )

    # Convert entities to response schemas
    customers_response = [
        BusinessPartnerResponse.model_validate(customer)
        for customer in result.customers
    ]

    return BusinessPartnerListResponse(
        customers=customers_response, pagination=pagination
    )
