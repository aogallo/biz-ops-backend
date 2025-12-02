from abc import ABC, abstractmethod

from app.internal.accounts.account_entity import Account


class AccountRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Account]:
        pass
