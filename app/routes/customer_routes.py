from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
from app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customer",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.get("/")
def list_customers(current_user=Depends(get_current_user)):
    """List all customers."""
    service = CustomerService(current_user=current_user)
    return service.list_all_customers()


# @router.post("/")
# def create_customer(
#     customer: CustomerCreate, current_user=Depends(get_current_user)
# ):
#     """Create a new customer."""
#     service = CustomerService(current_user=current_user)
#     return service.create_customer(customer=customer)
