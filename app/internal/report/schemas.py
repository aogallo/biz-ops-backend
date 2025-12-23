"""Schemas for report responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GeneralJournalEntry(BaseModel):
    """Schema for a single entry in the general journal report."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    date: datetime
    account_number: str = Field(serialization_alias="accountNumber")
    account_name: str = Field(serialization_alias="accountName")
    transaction_concept: str = Field(serialization_alias="transactionConcept")
    debit: float
    credit: float
    folio_number: int = Field(serialization_alias="folioNumber")


class GeneralJournalReport(BaseModel):
    """Schema for the complete general journal report."""

    entries: list[GeneralJournalEntry]
    total_debits: float = Field(serialization_alias="totalDebits")
    total_credits: float = Field(serialization_alias="totalCredits")
    count: int


class SalesLedgerEntry(BaseModel):
    """Schema for a single entry in the sales ledger report."""

    date: datetime
    type: str
    transaction_type: str = Field(serialization_alias="transtactionType")
    serie: str
    number_doc: str = Field(serialization_alias="numberDoc")
    nit: str
    name: str
    locally_taxed_goods: float
    locally_taxed_services: float
    locally_exempt_goods: float
    locally_exempt_services: float
    imported_taxed_goods: float
    imported_taxed_services: float
    imported_exempt_goods: float
    imported_exempt_services: float
    iva: float
    total: float


class SalesLedgerReport(BaseModel):
    entries: list[SalesLedgerEntry]
    count: int
