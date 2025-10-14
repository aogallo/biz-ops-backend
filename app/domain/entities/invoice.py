from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.customer import Customer
from app.domain.entities.journal_entry import JournalEntry


class InvoiceBase(SQLModel):
    date: datetime
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str

    company_id: int = Field(foreign_key="customer.id")
    customer_id: int = Field(foreign_key="customer.id")

    currency: str = "GTQ"
    amount: float

    state: str
    is_cancelled: bool | None = False
    cancelled_date: datetime | None = None

    iva: float | None = 0.0  # VAT amount
    petroleo: float | None = 0.0  # Petroleum tax
    turismo_hospedaje: float | None = 0.0  # Tourism lodging tax
    turismo_pasajes: float | None = 0.0  # Tourism transport tax
    timbre_prensa: float | None = 0.0  # Newspaper stamp tax
    bomberos: float | None = 0.0  # Firefighters tax
    tasa_municipal: float | None = 0.0  # Municipal rate
    bebidas_alcoholicas: float | None = 0.0  # Alcoholic beverages tax
    tabaco: float | None = 0.0  # Tobacco tax
    cemento: float | None = 0.0  # Cement tax
    bebidas_no_alcoholicas: float | None = 0.0  # Non-alcoholic beverages tax
    tarifa_portuaria: float | None = 0.0  # Port tariff

    # Relationships
    company: Customer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.company_id]"}
    )
    customer: Customer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.customer_id]"}
    )
    journal_entries: list[JournalEntry] = Relationship(
        back_populates="journal_entry"
    )


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
