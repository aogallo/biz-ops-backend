from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.customer.schema import CustomerListResponse, CustomerResponse
from app.internal.customer.service import CustomerService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all customers with pagination."""
    offset = calculate_offset(page=page, page_size=limit)

    service = CustomerService(session, current_user)
    result = service.list_all_customers(offset=offset, limit=limit)

    pagination = PaginationResponse(
        total=result.count,
        page_index=page - 1,
        page_size=limit,
    )

    # Convert entities to response schemas
    customers_response = [
        CustomerResponse.model_validate(customer)
        for customer in result.customers
    ]

    return CustomerListResponse(
        customers=customers_response, pagination=pagination
    )
