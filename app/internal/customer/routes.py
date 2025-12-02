from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
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
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all customers."""
    service = CustomerService(session, current_user)
    return service.list_all_customers()
