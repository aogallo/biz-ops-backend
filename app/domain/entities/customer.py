from datetime import UTC, datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CustomerBase(SQLModel):
    """
    Base customer
    """

    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str | None = Field(default=None)
    commercial_activity: str | None = Field(default=None)
    email: EmailStr
    address: str | None = Field(default=None)


class CustomerCreate(CustomerBase):
    """
    Create customer
    """

    pass


class Customer(CustomerBase, table=True):
    """
    Customer
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
