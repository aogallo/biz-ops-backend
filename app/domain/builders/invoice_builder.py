from datetime import UTC, datetime
from typing import Optional, List

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_detail import InvoiceDetail


class InvoiceBuilder:
    """Builder pattern for creating Invoice entities"""
    
    def __init__(self):
        self._invoice = Invoice()
        self._invoice.created_at = datetime.now(UTC)
        self._invoice.currency = "GTQ"
        self._invoice.subtotal = 0.0
        self._invoice.total_taxes = 0.0
        self._invoice.total_amount = 0.0
        self._invoice.is_cancelled = False
        self._invoice.details = []
    
    def with_date(self, date: datetime) -> "InvoiceBuilder":
        """Set invoice date"""
        self._invoice.date = date
        return self
    
    def with_authorization_number(self, auth_number: str) -> "InvoiceBuilder":
        """Set authorization number"""
        self._invoice.authorization_number = auth_number
        return self
    
    def with_dte_type(self, dte_type: str) -> "InvoiceBuilder":
        """Set DTE type"""
        self._invoice.dte_type = dte_type
        return self
    
    def with_serie(self, serie: str) -> "InvoiceBuilder":
        """Set invoice serie"""
        self._invoice.serie = serie
        return self
    
    def with_dte_number(self, dte_number: str) -> "InvoiceBuilder":
        """Set DTE number"""
        self._invoice.dte_number = dte_number
        return self
    
    def with_company_id(self, company_id: int) -> "InvoiceBuilder":
        """Set company ID"""
        self._invoice.company_id = company_id
        return self
    
    def with_customer_id(self, customer_id: int) -> "InvoiceBuilder":
        """Set customer ID"""
        self._invoice.customer_id = customer_id
        return self
    
    def with_currency(self, currency: str) -> "InvoiceBuilder":
        """Set invoice currency"""
        self._invoice.currency = currency
        return self
    
    def with_state(self, state: str) -> "InvoiceBuilder":
        """Set invoice state"""
        self._invoice.state = state
        return self
    
    def with_cancelled_status(self, is_cancelled: bool, cancelled_date: Optional[datetime] = None) -> "InvoiceBuilder":
        """Set cancelled status"""
        self._invoice.is_cancelled = is_cancelled
        if is_cancelled and cancelled_date:
            self._invoice.cancelled_date = cancelled_date
        return self
    
    def with_created_by(self, created_by: str) -> "InvoiceBuilder":
        """Set who created the invoice"""
        self._invoice.created_by = created_by
        return self
    
    def with_updated_by(self, updated_by: str) -> "InvoiceBuilder":
        """Set who updated the invoice"""
        self._invoice.updated_by = updated_by
        self._invoice.updated_at = datetime.now(UTC)
        return self
    
    def add_detail(self, detail: InvoiceDetail) -> "InvoiceBuilder":
        """Add an invoice detail"""
        self._invoice.details.append(detail)
        return self
    
    def add_details(self, details: List[InvoiceDetail]) -> "InvoiceBuilder":
        """Add multiple invoice details"""
        self._invoice.details.extend(details)
        return self
    
    def calculate_totals(self) -> "InvoiceBuilder":
        """Calculate invoice totals from details"""
        self._invoice.calculate_totals()
        return self
    
    def build(self) -> Invoice:
        """Build and return the invoice instance"""
        # Validate required fields
        if not self._invoice.date:
            raise ValueError("Invoice date is required")
        if not self._invoice.authorization_number:
            raise ValueError("Authorization number is required")
        if not self._invoice.dte_type:
            raise ValueError("DTE type is required")
        if not self._invoice.serie:
            raise ValueError("Invoice serie is required")
        if not self._invoice.dte_number:
            raise ValueError("DTE number is required")
        if not self._invoice.company_id:
            raise ValueError("Company ID is required")
        if not self._invoice.customer_id:
            raise ValueError("Customer ID is required")
        if not self._invoice.state:
            raise ValueError("Invoice state is required")
        if not self._invoice.created_by:
            raise ValueError("Created by is required")
        
        # Calculate totals if details exist
        if self._invoice.details:
            self._invoice.calculate_totals()
        
        return self._invoice
    
    @classmethod
    def create_invoice(
        cls,
        date: datetime,
        authorization_number: str,
        dte_type: str,
        serie: str,
        dte_number: str,
        company_id: int,
        customer_id: int,
        state: str,
        created_by: str,
        currency: str = "GTQ"
    ) -> Invoice:
        """Convenience method to create an invoice with required fields"""
        return (cls()
                .with_date(date)
                .with_authorization_number(authorization_number)
                .with_dte_type(dte_type)
                .with_serie(serie)
                .with_dte_number(dte_number)
                .with_company_id(company_id)
                .with_customer_id(customer_id)
                .with_currency(currency)
                .with_state(state)
                .with_created_by(created_by)
                .build())
