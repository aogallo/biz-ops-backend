from sqlmodel import Session, select

from app.internal.account.entity import Account, AccountCreate
from app.internal.account.repository import AccountRepository
from app.internal.user.entity import User


class AccountRepositoryImpl(AccountRepository):
    """Implementation of Account Repository"""

    def __init__(self, session: Session, current_user: User) -> None:
        self.db = session
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

    def get_by_id(self, id: int) -> Account | None:
        """Get an account by id"""
        return self.db.get(Account, id)

    def get_iva_credit_account(self) -> int | None:
        """Get IVA account"""
        statement = select(Account.id).where(
            Account.name == "CREDITO IMPUESTOS"
        )
        account_id: int | None = self.db.exec(statement).one_or_none()
        return account_id if account_id else None

    def get_default_payable_account(self) -> int | None:
        """Get default account payable"""
        statement = select(Account.id).where(
            Account.name == "CUENTAS POR PAGAR"
        )
        account_id: int | None = self.db.exec(statement).one_or_none()
        return account_id if account_id else None

    def get_default_receivable_account(self) -> int | None:
        """Get default account receivable"""
        statement = select(Account.id).where(Account.name == "CAJA")

        account_id: int | None = self.db.exec(statement).one_or_none()
        return account_id if account_id else None

    def get_iva_debit_account(self) -> int | None:
        """Get IVA debit account"""
        statement = select(Account.id).where(Account.name == "CAJA")

        account_id: int | None = self.db.exec(statement).one_or_none()
        return account_id if account_id else None
