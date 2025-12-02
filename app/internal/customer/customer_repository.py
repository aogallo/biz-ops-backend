from abc import ABC, abstractmethod

from app.internal.customer.customer_entity import Customer, CustomerCreate


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

    @abstractmethod
    def get_by_email(self, email: str) -> Customer | None:
        """
        Get all customers
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Customer | None:
        """
        Get customer by name
        """
        pass
