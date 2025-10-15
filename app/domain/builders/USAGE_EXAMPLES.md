# Invoice Builder Usage Examples

This document demonstrates how to use the refactored Invoice and InvoiceDetail builders.

## Basic Invoice with Line Items

### Method 1: Using with_header() for concise header setup

```python
from datetime import datetime
from app.domain.builders.invoice_builder import InvoiceBuilder
from app.domain.builders.invoice_detail_builder import InvoiceDetailBuilder

# Create an invoice with header and multiple line items
invoice = (
    InvoiceBuilder()
    .with_header(
        date=datetime.now(),
        authorization_number="AUTH-2025-001",
        dte_type="FACTURA",
        serie="A",
        dte_number="00001",
        company_id=1,
        customer_id=100,
        state="DRAFT",
        created_by="user@example.com",
        currency="GTQ"
    )
    .add_line(
        InvoiceDetailBuilder()
        .with_product("Laptop Dell XPS 15", code="LAPTOP-001")
        .with_price(quantity=2, unit_price=12000.00)
        .with_iva(2880.00)  # 12% IVA on total
        .with_created_by("user@example.com")
        .build()
    )
    .add_line(
        InvoiceDetailBuilder()
        .with_product("Mouse Logitech MX Master", code="MOUSE-001")
        .with_price(quantity=3, unit_price=450.00)
        .with_iva(162.00)
        .with_created_by("user@example.com")
        .build()
    )
    .build()
)

print(f"Invoice Total: {invoice.total_amount}")
print(f"Number of lines: {len(invoice.details)}")
```

### Method 2: Using individual header methods

```python
invoice = (
    InvoiceBuilder()
    .with_date(datetime.now())
    .with_authorization_number("AUTH-2025-001")
    .with_dte_type("FACTURA")
    .with_serie("A")
    .with_dte_number("00001")
    .with_company_id(1)
    .with_customer_id(100)
    .with_state("DRAFT")
    .with_currency("GTQ")
    .with_created_by("user@example.com")
    .add_line(...)
    .build()
)
```

### Method 3: Using the convenience static method

```python
# Set up header quickly and add lines
invoice = (
    InvoiceBuilder.create_invoice(
        date=datetime.now(),
        authorization_number="AUTH-2025-001",
        dte_type="FACTURA",
        serie="A",
        dte_number="00001",
        company_id=1,
        customer_id=100,
        state="DRAFT",
        created_by="user@example.com"
    )
    .add_line(...)
    .add_line(...)
    .build()
)
```

## Simple Line Items

### Method 1: Using add_simple_line() for basic items

```python
# Quick way to add simple line items
invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_simple_line(
        product_name="Laptop",
        quantity=1,
        unit_price=10000.00,
        created_by="user@example.com",
        product_code="LAP001",
        iva=1200.00
    )
    .add_simple_line(
        product_name="Mouse",
        quantity=2,
        unit_price=500.00,
        created_by="user@example.com",
        iva=120.00
    )
    .build()
)
```

## Complex Line Items with Multiple Taxes

```python
# Line item with multiple Guatemalan taxes
detail = (
    InvoiceDetailBuilder()
    .with_product(
        name="Gasolina Premium",
        code="GAS-001",
        description="Gasolina Premium 95 octanos"
    )
    .with_quantity(100.0)  # 100 gallons
    .with_unit_price(35.50)
    .with_iva(426.00)  # IVA 12%
    .with_petroleo(710.00)  # Petroleum tax
    .with_created_by("user@example.com")
    .build()
)

invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_line(detail)
    .build()
)

print(f"Line subtotal: {detail.subtotal}")
print(f"Line taxes: {detail.total_taxes}")
print(f"Line total: {detail.total}")
```

## Creating Multiple Details at Once

```python
# Create multiple line items
details = [
    InvoiceDetailBuilder.create_line(
        product_name="Product A",
        quantity=5,
        unit_price=100.0,
        created_by="user@example.com",
        iva=60.0
    ),
    InvoiceDetailBuilder.create_line(
        product_name="Product B",
        quantity=3,
        unit_price=200.0,
        created_by="user@example.com",
        iva=72.0
    ),
    InvoiceDetailBuilder.create_line(
        product_name="Product C",
        quantity=10,
        unit_price=50.0,
        created_by="user@example.com",
        iva=60.0
    ),
]

# Add all details at once
invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_lines(details)
    .build()
)
```

## Line Item with Tourism Taxes

```python
# Hotel invoice with tourism taxes
hotel_stay = (
    InvoiceDetailBuilder()
    .with_product(
        name="Habitación Doble - 3 noches",
        code="ROOM-DBL",
        description="Habitación doble con vista al mar"
    )
    .with_price(quantity=3, unit_price=850.00)
    .with_iva(306.00)  # IVA 12%
    .with_turismo_hospedaje(255.00)  # 10% tourism tax
    .with_created_by("reception@hotel.com")
    .build()
)

invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_line(hotel_stay)
    .build()
)
```

## Cancelled Invoice

```python
from datetime import datetime

# Create and cancel an invoice
invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_simple_line("Product", 1, 100.0, "user")
    .with_cancelled_status(
        is_cancelled=True,
        cancelled_date=datetime.now()
    )
    .build()
)

print(f"Is cancelled: {invoice.is_cancelled}")
print(f"Cancelled date: {invoice.cancelled_date}")
```

## Complete Real-World Example

```python
from datetime import datetime
from app.domain.builders.invoice_builder import InvoiceBuilder
from app.domain.builders.invoice_detail_builder import InvoiceDetailBuilder

# Create a complete invoice for a computer store
invoice = (
    InvoiceBuilder()
    .with_header(
        date=datetime(2025, 10, 15),
        authorization_number="SAT-2025-1234567890",
        dte_type="FACTURA",
        serie="A",
        dte_number="00125",
        company_id=1,
        customer_id=2050,
        state="POSTED",
        created_by="cashier01@store.com",
        currency="GTQ"
    )
    # Item 1: Laptops
    .add_line(
        InvoiceDetailBuilder()
        .with_product(
            name="Laptop Dell Inspiron 15",
            code="DELL-INS-15-001",
            description="Intel Core i7, 16GB RAM, 512GB SSD"
        )
        .with_price(quantity=2, unit_price=8500.00)
        .with_iva(2040.00)  # 12% IVA
        .with_created_by("cashier01@store.com")
        .build()
    )
    # Item 2: Monitors
    .add_line(
        InvoiceDetailBuilder()
        .with_product(
            name="Monitor Samsung 27\" 4K",
            code="SAM-MON-27-4K"
        )
        .with_price(quantity=2, unit_price=2800.00)
        .with_iva(672.00)
        .with_created_by("cashier01@store.com")
        .build()
    )
    # Item 3: Accessories (simple line)
    .add_simple_line(
        product_name="Cable HDMI 2.1 Premium",
        product_code="HDMI-21-PRE",
        quantity=2,
        unit_price=180.00,
        iva=43.20,
        created_by="cashier01@store.com"
    )
    .add_simple_line(
        product_name="Mouse Pad RGB",
        product_code="MPAD-RGB-001",
        quantity=2,
        unit_price=125.00,
        iva=30.00,
        created_by="cashier01@store.com"
    )
    .build()
)

# Display invoice summary
print(f"Invoice Number: {invoice.serie}-{invoice.dte_number}")
print(f"Customer ID: {invoice.customer_id}")
print(f"Date: {invoice.date}")
print(f"Currency: {invoice.currency}")
print(f"\nLine Items: {len(invoice.details)}")
for i, detail in enumerate(invoice.details, 1):
    print(f"\n{i}. {detail.product_name}")
    print(f"   Code: {detail.product_code}")
    print(f"   Qty: {detail.quantity} x {detail.unit_price:,.2f}")
    print(f"   Subtotal: {detail.subtotal:,.2f}")
    print(f"   IVA: {detail.iva:,.2f}")
    print(f"   Total: {detail.total:,.2f}")

print(f"\n{'='*50}")
print(f"Subtotal: Q{invoice.subtotal:,.2f}")
print(f"Taxes: Q{invoice.total_taxes:,.2f}")
print(f"TOTAL: Q{invoice.total_amount:,.2f}")
print(f"{'='*50}")
```

## Error Handling

```python
try:
    # Missing required fields will raise ValueError
    invoice = (
        InvoiceBuilder()
        .with_date(datetime.now())
        # Missing other required fields...
        .build()
    )
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # Invalid quantity
    detail = (
        InvoiceDetailBuilder()
        .with_product("Product")
        .with_quantity(-5)  # Invalid!
        .with_unit_price(100.0)
        .with_created_by("user")
        .build()
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

## Builder Pattern Benefits

1. **Fluent API**: Chain method calls for readability
2. **Validation**: Catch errors before creating entities
3. **Flexibility**: Mix and match header and line construction methods
4. **Type Safety**: Full type hints for IDE support
5. **Separation of Concerns**: Header vs line items clearly separated
6. **Reusability**: Use InvoiceDetailBuilder independently

## Best Practices

1. **Always call `.build()` last** to create the final entity
2. **Use `.with_header()` for concise header setup** when possible
3. **Use `.add_simple_line()` for basic items** without complex taxes
4. **Use `InvoiceDetailBuilder` directly** for complex line items
5. **Set `created_by`** for both invoice and line items
6. **Let the builders calculate totals** automatically via `.build()`

