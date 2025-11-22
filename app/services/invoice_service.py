from app.domain.entities.user import User
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)


class InvoiceService:
    """Service for managing invoices."""

    def __init__(self, current_user: User) -> None:
        self.repository = CustomerRepositoryImpl(current_user)

    def list_all_invoices(self):
        return self.repository.get_all_customers()
