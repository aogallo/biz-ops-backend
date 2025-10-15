from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.invoice_detail import InvoiceDetail, InvoiceDetailCreate
from app.domain.repositories.base_repository import BaseRepository


class InvoiceDetailRepository(BaseRepository[InvoiceDetail], ABC):
    """Invoice detail repository interface extending BaseRepository"""
    
    @abstractmethod
    def create_detail(self, detail: InvoiceDetailCreate) -> InvoiceDetail:
        """Create a new invoice detail using InvoiceDetailCreate schema"""
        pass

    @abstractmethod
    def get_details_by_invoice(self, invoice_id: int) -> List[InvoiceDetail]:
        """Get all details for a specific invoice"""
        pass

    @abstractmethod
    def get_details_by_product(self, product_code: str) -> List[InvoiceDetail]:
        """Get all details for a specific product"""
        pass

    @abstractmethod
    def update_detail_taxes(self, detail_id: int, taxes: dict) -> InvoiceDetail:
        """Update tax amounts for a detail"""
        pass

    @abstractmethod
    def bulk_create_details(self, details: List[InvoiceDetailCreate]) -> List[InvoiceDetail]:
        """Create multiple invoice details at once"""
        pass
