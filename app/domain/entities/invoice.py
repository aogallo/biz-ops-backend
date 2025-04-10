from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Invoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
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
    is_cancelled: Optional[bool] = False
    cancelled_date: Optional[datetime] = None

    iva: Optional[float] = 0.0  # VAT amount
    petroleo: Optional[float] = 0.0  # Petroleum tax
    turismo_hospedaje: Optional[float] = 0.0  # Tourism lodging tax
    turismo_pasajes: Optional[float] = 0.0  # Tourism transport tax
    timbre_prensa: Optional[float] = 0.0  # Newspaper stamp tax
    bomberos: Optional[float] = 0.0  # Firefighters tax
    tasa_municipal: Optional[float] = 0.0  # Municipal rate
    bebidas_alcoholicas: Optional[float] = 0.0  # Alcoholic beverages tax
    tabaco: Optional[float] = 0.0  # Tobacco tax
    cemento: Optional[float] = 0.0  # Cement tax
    bebidas_no_alcoholicas: Optional[float] = 0.0  # Non-alcoholic beverages tax
    tarifa_portuaria: Optional[float] = 0.0  # Port tariff

    # Relationships
    emisor: "Customer" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.emisor_id]"}
    )
    receptor: "Customer" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.receptor_id]"}
    )
