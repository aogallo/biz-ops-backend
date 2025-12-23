from datetime import UTC, datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str | None = Field(default=None)
    commercial_activity: str | None = Field(default=None)
    email: EmailStr | None = Field(
        default="no-email@example.com", nullable=True
    )
    address: str | None = Field(default=None)
    managed_by_accountant: bool = Field(default=False, index=True)


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)


class CompanyCreate(CompanyBase):
    pass
