from datetime import datetime

from sqlmodel import select

from app.domain.entities.invoice import Invoice
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.infrastructure.database import get_current_session
from app.schemas.invoice_schema import InvoiceCreate


class InvoiceRepositoryImpl(InvoiceRepository):
    """Implementation of Invoice Repository"""

    def __init__(self) -> None:
        self.db = get_current_session()

    def create_invoice(self, invoice: InvoiceCreate) -> Invoice:
        new_invoice: Invoice = Invoice.model_validate(invoice)
        self.db.add(new_invoice)
        self.db.commit()
        self.db.refresh(new_invoice)
        return new_invoice

    def get_invoice_by_number(
        self, dte_number: str, serie: str
    ) -> Invoice | None:
        """Get an invoice by DTE number and serie"""
        statement = select(Invoice).where(
            Invoice.dte_number == dte_number, Invoice.serie == serie
        )
        result: Invoice | None = self.db.exec(statement).one_or_none()
        return result

    def get_cancelled_invoices(self) -> list[Invoice]:
        """Get all cancelled invoices"""
        statement = select(Invoice).where(bool(Invoice.is_cancelled))
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def get_invoices_by_customer(self, customer_id: int) -> list[Invoice]:
        """Get all invoices by customer"""
        statement = select(Invoice).where(Invoice.customer_id == customer_id)
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def get_invoices_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Invoice]:
        """Get all invoices by date range"""
        statement = select(Invoice).where(
            Invoice.date >= start_date, Invoice.date <= end_date
        )
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def cancel_invoice(self, invoice_id: int, cancelled_by: str) -> bool:
        """Cancel an invoice"""
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice: Invoice | None = self.db.exec(statement).one_or_none()
        if invoice:
            invoice.is_cancelled = True
            invoice.cancelled_by = cancelled_by
            self.db.commit()
            return True
        return False

    def get_all(self) -> list[Invoice]:
        """Get all invoices"""
        statement = select(Invoice)
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def add_bulk(self, invoices: list[Invoice]):
        """Add bulk invoices"""
        self.db.add_all(invoices)
        self.db.commit()
        for invoice in invoices:
            self.db.refresh(invoice)
        return invoices

    def get_invoice_by_serie_and_dte(
        self, serie: str, dte_number: int
    ) -> Invoice | None:
        """Get invoice by serie and dte number"""
        statement = select(Invoice).where(
            Invoice.serie == serie, Invoice.dte_number == dte_number
        )
        result: Invoice | None = self.db.exec(statement).one_or_none()
        return result
