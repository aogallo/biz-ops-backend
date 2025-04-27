from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class AccountBase(SQLModel):
    account_number: str = Field(unique=True)
    name: str
    type: str


class AccountCreate(AccountBase):
    pass


class Account(AccountBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)
