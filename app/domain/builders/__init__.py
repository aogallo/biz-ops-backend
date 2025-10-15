"""Builder patterns for domain entities.

This package provides fluent builder patterns for constructing complex domain entities
with proper validation and automatic calculation of derived fields.

Example usage:
    from app.domain.builders import InvoiceBuilder, InvoiceDetailBuilder

    invoice = (
        InvoiceBuilder()
        .with_header(...)
        .add_line(
            InvoiceDetailBuilder()
            .with_product("Product A")
            .with_price(2, 100.0)
            .with_iva(24.0)
            .with_created_by("user")
            .build()
        )
        .build()
    )
"""

from app.domain.builders.invoice_builder import InvoiceBuilder
from app.domain.builders.invoice_detail_builder import InvoiceDetailBuilder

__all__ = ["InvoiceBuilder", "InvoiceDetailBuilder"]
