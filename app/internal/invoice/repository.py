from abc import ABC, abstractmethod
from datetime import datetime

from app.internal.invoice.entity import Invoice
from app.internal.invoice.schema import InvoiceCreate


class InvoiceRepository(ABC):
    """Invoice repository interface"""

    @abstractmethod
    def create_invoice(self, invoice: InvoiceCreate) -> Invoice:
        """Create a new invoice"""
        pass

    @abstractmethod
    def get_invoice_by_number(
        self, dte_number: str, serie: str
    ) -> Invoice | None:
        """Get an invoice by DTE number and serie"""
        pass

    @abstractmethod
    def get_invoices_by_customer(self, customer_id: int) -> list[Invoice]:
        """Get all invoices by customer"""
        pass

    @abstractmethod
    def get_invoices_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Invoice]:
        """Get all invoices by date range"""
        pass

    @abstractmethod
    def get_cancelled_invoices(self) -> list[Invoice]:
        """Get all cancelled invoices by date range"""
        pass

    @abstractmethod
    def cancel_invoice(self, invoice_id: int, cancelled_by: str) -> bool:
        """Cancel an invoice by id"""
        pass
