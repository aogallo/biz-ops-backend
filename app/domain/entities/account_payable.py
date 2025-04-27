from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.customer import Customer


# cuenta por pagar
class AccountPayable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="customer.id")
    amount: float

    company: Customer = Relationship(back_populates="customer")

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None)
