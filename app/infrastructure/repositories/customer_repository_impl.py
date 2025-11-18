from sqlmodel import Session, select

from app.domain.entities.customer import Customer, CustomerCreate
from app.domain.repositories.customer_repository import CustomerRepository
from app.infrastructure.database import get_current_session


class CustomerRepositoryImpl(CustomerRepository):
    def __init__(self, session: Session | None = None) -> None:
        self.db = session or get_current_session()

    def create(self, customer_create: CustomerCreate) -> Customer:
        customer: Customer = Customer.model_validate(customer_create)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_all_customers(self) -> list[Customer]:
        statement = select(Customer)
        result: list[Customer] = list(self.db.exec(statement))
        return result

    def get_by_id(self, id: int) -> Customer | None:
        statement = select(Customer).where(Customer.id == id)
        result: Customer | None = self.db.exec(statement).one_or_none()
        return result
