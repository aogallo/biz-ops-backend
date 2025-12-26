from uuid import UUID

from sqlmodel import Session, func, select

from app.internal.account.entity import Account, AccountCreate
from app.internal.account.repository import AccountRepository
from app.internal.user.entity import User


class AccountRepositoryImpl(AccountRepository):
    """
    Implementation of Account Repository.
    All queries are automatically scoped to organization_id for multi-tenancy.
    Accounts are organization-scoped (shared across companies).
    """

    def __init__(
        self, session: Session, current_user: User, organization_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.organization_id = (
            organization_id  # Organization context for multi-tenancy
        )

    def get_all(self) -> list[Account]:
        """Get all accounts (scoped to organization)"""
        statement = select(Account).where(
            Account.organization_id == self.organization_id
        )
        accounts: list[Account] = list(self.db.exec(statement))
        return accounts

    def create(self, account: AccountCreate) -> Account:
        """Create a new account scoped to this organization"""
        new_account: Account = Account.model_validate(
            account,
            update={
                "organization_id": self.organization_id,
                "created_by": self.current_user.auth0_user_id,
            },
        )
        self.db.add(new_account)
        self.db.commit()
        self.db.refresh(new_account)
        return new_account

    def get_by_id(self, account_id: UUID) -> Account | None:
        """Get an account by id (scoped to organization)"""
        statement = select(Account).where(
            Account.organization_id == self.organization_id,
            Account.id == account_id,
        )
        account: Account | None = self.db.exec(statement).one_or_none()
        return account

    def get_by_name(self, name: str) -> Account | None:
        """Get an account by name (scoped to organization)"""
        statement = select(Account).where(
            Account.organization_id == self.organization_id,
            Account.name == name,
        )
        account: Account | None = self.db.exec(statement).one_or_none()
        return account

    def get_by_code(self, code: str) -> Account | None:
        """Get an account by code (scoped to organization)"""
        statement = select(Account).where(
            Account.organization_id == self.organization_id,
            Account.code == code,
        )
        account: Account | None = self.db.exec(statement).one_or_none()
        return account

    def delete(self, account_id: UUID) -> bool:
        """Delete an account by id (scoped to organization)"""
        account = self.get_by_id(account_id)
        if account is None:
            return False
        self.db.delete(account)
        self.db.commit()
        return True

    def update(self, account: Account) -> Account:
        """Update an account (must belong to this organization)"""
        # Verify account belongs to this organization
        if account.organization_id != self.organization_id:
            raise ValueError(
                f"Account does not belong to organization {self.organization_id}"
            )

        account.updated_by = self.current_user.auth0_user_id
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get_count(self) -> int:
        """Get count of accounts (scoped to organization)"""
        count_statement = (
            select(func.count())
            .select_from(Account)
            .where(Account.organization_id == self.organization_id)
        )
        count: int = self.db.exec(count_statement).one()
        return count
