from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.invoice import Invoice, InvoiceCreate
from app.domain.repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[Invoice], ABC):
    """Invoice repository interface extending BaseRepository"""

    @abstractmethod
    def create_invoice(self, invoice: InvoiceCreate) -> Invoice:
        """Create a new invoice using InvoiceCreate schema"""
        pass

    @abstractmethod
    def get_invoice_by_number(
        self, dte_number: str, serie: str
    ) -> Invoice | None:
        """Get invoice by DTE number and serie"""
        pass

    @abstractmethod
    def get_invoices_by_customer(self, customer_id: int) -> list[Invoice]:
        """Get all invoices for a specific customer"""
        pass

    @abstractmethod
    def get_invoices_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Invoice]:
        """Get invoices within a date range"""
        pass

    @abstractmethod
    def get_cancelled_invoices(self) -> list[Invoice]:
        """Get all cancelled invoices"""
        pass

    @abstractmethod
    def cancel_invoice(self, invoice_id: int, cancelled_by: str) -> bool:
        """Cancel an invoice"""
        pass
