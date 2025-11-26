from sqlmodel import col, select

from app.domain.entities.customer import Customer, CustomerCreate
from app.domain.entities.user import User
from app.domain.repositories.customer_repository import CustomerRepository
from app.infrastructure.database import get_current_session


class CustomerRepositoryImpl(CustomerRepository):
    def __init__(self, current_user: User) -> None:
        self.db = get_current_session()
        self.current_user = current_user

    def create(self, customer_create: CustomerCreate) -> Customer:
        customer: Customer = Customer.model_validate(
            customer_create, update={"created_by": self.current_user.auth_id}
        )
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

    def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        result: Customer | None = self.db.exec(statement).one_or_none()
        return result

    def get_by_name(self, name: str) -> Customer | None:
        statement = select(Customer).where(Customer.name == name)
        result: Customer | None = self.db.exec(statement).one_or_none()
        return result

    def get_names(self, company_names: list[str]):
        statement = select(Customer).where(
            col(Customer.name).in_(company_names)
        )
        results: list[Customer] = list(self.db.exec(statement).all())
        return results

    def get_customers_by_nit(self, customers) -> list[Customer]:
        """Get existing customers by NIT"""
        nits = [c["nit"] for c in customers]
        statement = select(Customer).where(col(Customer.nit).in_(nits))
        result: list[Customer] = self.db.exec(statement)._allrows()
        return list(result)

    def add_bulk(self, customers: list[Customer]):
        """Add bulk customers"""
        self.db.add_all(customers)
        self.db.commit()
        for customer in customers:
            self.db.refresh(customer)

    def get_by_nit(self, nit: str) -> Customer | None:
        """Get customer by NIT"""
        statement = select(Customer).where(Customer.nit == nit)
        result: Customer | None = self.db.exec(statement).one_or_none()
        return result
