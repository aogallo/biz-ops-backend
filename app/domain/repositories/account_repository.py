from abc import ABC, abstractmethod

from app.domain.entities.account import Account


class AccountRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Account]:
        pass
