from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.account.entity import Account, AccountCreate
from app.internal.account.respository_impl import AccountRepositoryImpl
from app.internal.user.entity import User


class AccountService:
    """Service for managing accounts."""

    def __init__(self, session: Session, current_user: User) -> None:
        self.account_repo = AccountRepositoryImpl(session, current_user)

    def list_accounts(self) -> list[Account]:
        """List all accounts"""
        return self.account_repo.get_all()

    def create_account(self, account_request: AccountCreate) -> Account:
        """
        Create a new account.
        Raises error if account with same number exists.
        """
        db_account = self.account_repo.get_account_by_number(
            account_request.account_number
        )

        if db_account is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already exitst",
            )

        return self.account_repo.create(account_request)
