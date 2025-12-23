from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.customer.entity import CustomerCreate
from app.internal.customer.repository_impl import CustomerRepositoryImpl
from app.internal.customer.service_schemas import CustomerListServiceResponse
from app.internal.user.entity import User


class CustomerService:
    """Service for managing customers."""

    def __init__(self, session: Session, current_user: User) -> None:
        self.repository = CustomerRepositoryImpl(session, current_user)

    def create_customer(self, customer: CustomerCreate):
        """
        Create a new customer.
        Raises error if customer with same email exists.
        """
        existed_customer = self.repository.get_by_nit(customer.nit)

        if existed_customer is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer already exists",
            )

        return self.repository.create(customer)

    def list_all_customers(
        self, offset: int, limit: int
    ) -> CustomerListServiceResponse:
        """
        List all customers with pagination.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            CustomerListServiceResponse: Validated response with count and
                customers

        Raises:
            HTTPException: If database query fails
        """
        customers = self.repository.get_all_customers(
            offset=offset, limit=limit
        )
        count = self.repository.get_count()

        return CustomerListServiceResponse(count=count, customers=customers)
