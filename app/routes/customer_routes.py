from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
from app.schemas.customer_schema import CustomerListResponse, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.get("/", response_model=CustomerListResponse)
def list_customers(current_user=Depends(get_current_user)):
    """List all customers."""
    service = CustomerService(current_user=current_user)
    customers = service.list_all_customers()
    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=len(customers),
    )


# @router.post("/")
# def create_customer(
#     customer: CustomerCreate, current_user=Depends(get_current_user)
# ):
#     """Create a new customer."""
#     service = CustomerService(current_user=current_user)
#     return service.create_customer(customer=customer)
