from sqlmodel import select

from app.domain.entities.account import Account, AccountCreate
from app.domain.entities.user import User
from app.domain.repositories.account_repository import AccountRepository
from app.infrastructure.database import get_current_session


class AccountRepositoryImpl(AccountRepository):
    """Implementation of Account Repository"""

    def __init__(self, current_user: User) -> None:
        self.db = get_current_session()
        self.current_user = current_user

    def get_all(self) -> list[Account]:
        statement = select(Account)
        result: list[Account] = list(self.db.exec(statement))
        return result

    def create(self, account: AccountCreate) -> Account:
        """Create a new account"""
        # Convert entity to dict and add created_by
        account_data = account.model_dump()
        account_data["created_by"] = self.current_user.auth_id

        # Create Account instance
        new_account = Account(**account_data)
        self.db.add(new_account)
        self.db.commit()
        self.db.refresh(new_account)
        return new_account

    def get_account_by_number(self, number: str) -> Account | None:
        """Get an account by number"""
        statement = select(Account).where(Account.account_number == number)
        account: Account | None = self.db.exec(
            statement=statement
        ).one_or_none()
        return account
