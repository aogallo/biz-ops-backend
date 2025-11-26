from fastapi import HTTPException, status

from app.domain.entities.customer import CustomerCreate
from app.domain.entities.user import User
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)


class CustomerService:
    """Service for managing customers."""

    def __init__(self, current_user: User) -> None:
        self.repository = CustomerRepositoryImpl(current_user=current_user)

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

    def list_all_customers(self):
        """List all customers."""
        return self.repository.get_all_customers()
