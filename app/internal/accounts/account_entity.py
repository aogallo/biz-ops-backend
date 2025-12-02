from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class AccountBase(SQLModel):
    """
    Base account
    """

    account_number: str = Field(unique=True)
    name: str
    type: str


class AccountCreate(AccountBase):
    """
    Create account
    """

    pass


class Account(AccountBase, table=True):
    """
    Account
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
