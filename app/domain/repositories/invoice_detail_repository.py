from abc import ABC, abstractmethod

from app.domain.entities.invoice_detail import (
    InvoiceDetail,
    InvoiceDetailCreate,
)


class InvoiceDetailRepository(ABC):
    """Invoice detail repository interface extending BaseRepository"""

    @abstractmethod
    def create_detail(self, detail: InvoiceDetailCreate) -> InvoiceDetail:
        """Create a new invoice detail using InvoiceDetailCreate schema"""
        pass

    @abstractmethod
    def get_details_by_invoice(self, invoice_id: int) -> list[InvoiceDetail]:
        """Get all details for a specific invoice"""
        pass

    @abstractmethod
    def get_details_by_product(self, product_code: str) -> list[InvoiceDetail]:
        """Get all details for a specific product"""
        pass

    @abstractmethod
    def update_detail_taxes(
        self, detail_id: int, taxes: dict
    ) -> InvoiceDetail:
        """Update tax amounts for a detail"""
        pass

    @abstractmethod
    def bulk_create_details(
        self, details: list[InvoiceDetailCreate]
    ) -> list[InvoiceDetail]:
        """Create multiple invoice details at once"""
        pass
