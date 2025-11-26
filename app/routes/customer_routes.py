from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
from app.schemas.customer_schema import CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.get("", response_model=list[CustomerResponse])
def list_customers(current_user=Depends(get_current_user)):
    """List all customers."""
    service = CustomerService(current_user=current_user)
    return service.list_all_customers()
