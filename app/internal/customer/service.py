from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.customer.entity import CustomerCreate
from app.internal.customer.repository_impl import CustomerRepositoryImpl
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

    def list_all_customers(self):
        """List all customers."""
        return self.repository.get_all_customers()
