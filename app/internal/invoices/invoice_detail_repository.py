from abc import ABC, abstractmethod

from app.internal.invoices.invoice_detail_entity import (
    InvoiceDetail,
    InvoiceDetailCreate,
)


class InvoiceDetailRepository(ABC):
    """Invoice detail repository interface"""

    @abstractmethod
    def create_detail(self, detail: InvoiceDetailCreate) -> InvoiceDetail:
        """Create a new invoice detail"""
        pass

    @abstractmethod
    def get_details_by_invoice(self, invoice_id: int) -> list[InvoiceDetail]:
        """Get all details by invoice"""
        pass

    @abstractmethod
    def get_details_by_product(self, product_code: str) -> list[InvoiceDetail]:
        """Get all details by product"""
        pass

    @abstractmethod
    def update_detail_taxes(
        self, detail_id: int, taxes: dict
    ) -> InvoiceDetail:
        """Update tax amounts by detail id"""
        pass

    @abstractmethod
    def bulk_create_details(
        self, details: list[InvoiceDetailCreate]
    ) -> list[InvoiceDetail]:
        """Create multiple invoice details"""
        pass
