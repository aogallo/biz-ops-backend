from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.customer.schema import CustomerResponse
from app.internal.customer.service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all customers."""
    offset = page - 1
    if offset > 0:
        offset *= 10
    service = CustomerService(session, current_user)
    return service.list_all_customers(offset=offset, limit=limit)
