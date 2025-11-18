from abc import ABC, abstractmethod

from app.domain.entities.customer import Customer, CustomerCreate


class CustomerRepository(ABC):
    """
    Customer repository
    """

    @abstractmethod
    def create(self, customer_create: CustomerCreate) -> Customer:
        """
        Create a customer
        """
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Customer | None:
        """
        Get a customer by id
        """
        pass

    @abstractmethod
    def get_all_customers(self) -> list[Customer]:
        """
        Get all customers
        """
        pass
