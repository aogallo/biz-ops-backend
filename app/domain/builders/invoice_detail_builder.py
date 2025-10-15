from datetime import UTC, datetime
from typing import Optional

from app.domain.entities.invoice_detail import InvoiceDetail


class InvoiceDetailBuilder:
    """Builder pattern for creating InvoiceDetail entities"""
    
    def __init__(self):
        self._detail = InvoiceDetail()
        self._detail.created_at = datetime.now(UTC)
        self._detail.quantity = 1.0
        self._detail.unit_price = 0.0
        self._detail.subtotal = 0.0
        self._detail.total_taxes = 0.0
        self._detail.total = 0.0
        # Initialize all tax fields to 0
        self._detail.iva = 0.0
        self._detail.petroleo = 0.0
        self._detail.turismo_hospedaje = 0.0
        self._detail.turismo_pasajes = 0.0
        self._detail.timbre_prensa = 0.0
        self._detail.bomberos = 0.0
        self._detail.tasa_municipal = 0.0
        self._detail.bebidas_alcoholicas = 0.0
        self._detail.tabaco = 0.0
        self._detail.cemento = 0.0
        self._detail.bebidas_no_alcoholicas = 0.0
        self._detail.tarifa_portuaria = 0.0
    
    def with_invoice_id(self, invoice_id: int) -> "InvoiceDetailBuilder":
        """Set invoice ID"""
        self._detail.invoice_id = invoice_id
        return self
    
    def with_product_code(self, product_code: str) -> "InvoiceDetailBuilder":
        """Set product code"""
        self._detail.product_code = product_code
        return self
    
    def with_product_name(self, product_name: str) -> "InvoiceDetailBuilder":
        """Set product name"""
        self._detail.product_name = product_name
        return self
    
    def with_description(self, description: str) -> "InvoiceDetailBuilder":
        """Set product description"""
        self._detail.description = description
        return self
    
    def with_quantity(self, quantity: float) -> "InvoiceDetailBuilder":
        """Set quantity"""
        self._detail.quantity = quantity
        return self
    
    def with_unit_price(self, unit_price: float) -> "InvoiceDetailBuilder":
        """Set unit price"""
        self._detail.unit_price = unit_price
        return self
    
    def with_iva(self, iva: float) -> "InvoiceDetailBuilder":
        """Set IVA (VAT) amount"""
        self._detail.iva = iva
        return self
    
    def with_petroleo(self, petroleo: float) -> "InvoiceDetailBuilder":
        """Set petroleum tax"""
        self._detail.petroleo = petroleo
        return self
    
    def with_turismo_hospedaje(self, turismo_hospedaje: float) -> "InvoiceDetailBuilder":
        """Set tourism lodging tax"""
        self._detail.turismo_hospedaje = turismo_hospedaje
        return self
    
    def with_turismo_pasajes(self, turismo_pasajes: float) -> "InvoiceDetailBuilder":
        """Set tourism transport tax"""
        self._detail.turismo_pasajes = turismo_pasajes
        return self
    
    def with_timbre_prensa(self, timbre_prensa: float) -> "InvoiceDetailBuilder":
        """Set newspaper stamp tax"""
        self._detail.timbre_prensa = timbre_prensa
        return self
    
    def with_bomberos(self, bomberos: float) -> "InvoiceDetailBuilder":
        """Set firefighters tax"""
        self._detail.bomberos = bomberos
        return self
    
    def with_tasa_municipal(self, tasa_municipal: float) -> "InvoiceDetailBuilder":
        """Set municipal rate"""
        self._detail.tasa_municipal = tasa_municipal
        return self
    
    def with_bebidas_alcoholicas(self, bebidas_alcoholicas: float) -> "InvoiceDetailBuilder":
        """Set alcoholic beverages tax"""
        self._detail.bebidas_alcoholicas = bebidas_alcoholicas
        return self
    
    def with_tabaco(self, tabaco: float) -> "InvoiceDetailBuilder":
        """Set tobacco tax"""
        self._detail.tabaco = tabaco
        return self
    
    def with_cemento(self, cemento: float) -> "InvoiceDetailBuilder":
        """Set cement tax"""
        self._detail.cemento = cemento
        return self
    
    def with_bebidas_no_alcoholicas(self, bebidas_no_alcoholicas: float) -> "InvoiceDetailBuilder":
        """Set non-alcoholic beverages tax"""
        self._detail.bebidas_no_alcoholicas = bebidas_no_alcoholicas
        return self
    
    def with_tarifa_portuaria(self, tarifa_portuaria: float) -> "InvoiceDetailBuilder":
        """Set port tariff"""
        self._detail.tarifa_portuaria = tarifa_portuaria
        return self
    
    def with_created_by(self, created_by: str) -> "InvoiceDetailBuilder":
        """Set who created the detail"""
        self._detail.created_by = created_by
        return self
    
    def with_updated_by(self, updated_by: str) -> "InvoiceDetailBuilder":
        """Set who updated the detail"""
        self._detail.updated_by = updated_by
        self._detail.updated_at = datetime.now(UTC)
        return self
    
    def calculate_totals(self) -> "InvoiceDetailBuilder":
        """Calculate subtotal, total taxes, and total"""
        self._detail.calculate_totals()
        return self
    
    def build(self) -> InvoiceDetail:
        """Build and return the invoice detail instance"""
        # Validate required fields
        if not self._detail.invoice_id:
            raise ValueError("Invoice ID is required")
        if not self._detail.product_name:
            raise ValueError("Product name is required")
        if self._detail.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if self._detail.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if not self._detail.created_by:
            raise ValueError("Created by is required")
        
        # Calculate totals
        self._detail.calculate_totals()
        
        return self._detail
    
    @classmethod
    def create_detail(
        cls,
        invoice_id: int,
        product_name: str,
        quantity: float,
        unit_price: float,
        created_by: str,
        product_code: Optional[str] = None,
        description: Optional[str] = None,
        iva: float = 0.0
    ) -> InvoiceDetail:
        """Convenience method to create an invoice detail with required fields"""
        builder = (cls()
                   .with_invoice_id(invoice_id)
                   .with_product_name(product_name)
                   .with_quantity(quantity)
                   .with_unit_price(unit_price)
                   .with_created_by(created_by)
                   .with_iva(iva))
        
        if product_code:
            builder.with_product_code(product_code)
        if description:
            builder.with_description(description)
        
        return builder.build()
    
    @classmethod
    def create_service_detail(
        cls,
        invoice_id: int,
        service_name: str,
        quantity: float,
        unit_price: float,
        created_by: str,
        description: Optional[str] = None,
        iva: float = 0.0
    ) -> InvoiceDetail:
        """Convenience method to create a service detail (no product code)"""
        return cls.create_detail(
            invoice_id=invoice_id,
            product_name=service_name,
            quantity=quantity,
            unit_price=unit_price,
            created_by=created_by,
            description=description,
            iva=iva
        )
