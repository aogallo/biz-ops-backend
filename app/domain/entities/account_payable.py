from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.customer import Customer


class AccountPayableBase(SQLModel):
    """
    Base account payable
    """

    company_id: int = Field(foreign_key="customer.id")
    amount: float

    company: Customer = Relationship(back_populates="customer")


class AccountPayableCreate(AccountPayableBase):
    """
    Create account payable
    """

    pass


# cuenta por pagar
class AccountPayable(AccountPayableBase, table=True):
    """
    Account payable
    """

    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
