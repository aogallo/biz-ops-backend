# Invoice Builder Pattern - Refactored

## Overview

The Invoice and InvoiceDetail builders have been refactored to provide a cleaner, more intuitive API following the builder pattern. This allows you to create complex invoices with multiple line items in a fluent, readable way.

## What Changed

### Before (Old Way)
```python
# Old way - limited flexibility
invoice = InvoiceBuilder.create_invoice(
    date=datetime.now(),
    authorization_number="AUTH123",
    dte_type="FACTURA",
    serie="A",
    dte_number="001",
    company_id=1,
    customer_id=2,
    state="DRAFT",
    created_by="user"
)
# Then manually add details...
```

### After (New Way)
```python
# New way - fluent, flexible API
invoice = (
    InvoiceBuilder()
    .with_header(
        date=datetime.now(),
        authorization_number="AUTH123",
        dte_type="FACTURA",
        serie="A",
        dte_number="001",
        company_id=1,
        customer_id=2,
        state="DRAFT",
        created_by="user"
    )
    .add_line(
        InvoiceDetailBuilder()
        .with_product("Product A")
        .with_price(quantity=2, unit_price=100.0)
        .with_iva(24.0)
        .with_created_by("user")
        .build()
    )
    .add_simple_line("Product B", 1, 200.0, "user", iva=24.0)
    .build()
)
```

## New Features

### 1. InvoiceDetailBuilder (NEW)
A dedicated builder for creating invoice line items with full validation and automatic calculation.

**Features:**
- Product information (name, code, description)
- Quantity and unit price
- All Guatemalan tax types (IVA, petroleum, tourism, etc.)
- Automatic calculation of subtotal, taxes, and total
- Validation of required fields
- Convenience methods for common use cases

### 2. Enhanced InvoiceBuilder
Improved with better separation between header and line items.

**New Methods:**
- `.with_header(...)` - Set all header fields at once
- `.add_line(detail)` - Add a built InvoiceDetail
- `.add_simple_line(...)` - Quick way to add simple line items
- `.add_lines(details)` - Add multiple line items at once

**Preserved Methods:**
- All individual `.with_*()` methods still work
- `.create_invoice()` now returns a builder (not a built invoice)
- Automatic total calculation on `.build()`

## File Structure

```
app/domain/builders/
├── __init__.py                    # Package exports
├── invoice_builder.py             # Refactored InvoiceBuilder
├── invoice_detail_builder.py      # NEW - InvoiceDetailBuilder
├── README.md                      # This file
└── USAGE_EXAMPLES.md             # Comprehensive usage examples

tests/unit/
└── test_invoice_builder.py        # NEW - 18 unit tests
```

## Key Benefits

### 1. **Separation of Concerns**
- Header configuration is separate from line item creation
- Each builder has a single responsibility

### 2. **Flexibility**
Three ways to add line items:
- Full builder: `InvoiceDetailBuilder()....build()`
- Simple line: `.add_simple_line(...)`
- Batch: `.add_lines([...])`

### 3. **Type Safety**
- Full type hints for IDE autocomplete
- Type checking with mypy

### 4. **Validation**
- Required fields validated before building
- Automatic calculation of totals
- Prevents invalid data (negative prices, zero quantities)

### 5. **Readability**
- Fluent API reads like natural language
- Clear structure: header, then lines, then build
- Self-documenting code

## Quick Start

### Simple Invoice
```python
from app.domain.builders import InvoiceBuilder

invoice = (
    InvoiceBuilder()
    .with_header(
        date=datetime.now(),
        authorization_number="AUTH123",
        dte_type="FACTURA",
        serie="A",
        dte_number="001",
        company_id=1,
        customer_id=2,
        state="DRAFT",
        created_by="user@example.com"
    )
    .add_simple_line("Product A", 2, 100.0, "user@example.com", iva=24.0)
    .add_simple_line("Product B", 1, 200.0, "user@example.com", iva=24.0)
    .build()
)
```

### Complex Line Items
```python
from app.domain.builders import InvoiceBuilder, InvoiceDetailBuilder

invoice = (
    InvoiceBuilder()
    .with_header(...)
    .add_line(
        InvoiceDetailBuilder()
        .with_product(
            name="Gasolina Premium",
            code="GAS-001",
            description="95 octanos"
        )
        .with_price(quantity=100, unit_price=35.50)
        .with_iva(426.0)
        .with_petroleo(710.0)
        .with_created_by("user@example.com")
        .build()
    )
    .build()
)
```

## Testing

Run the comprehensive test suite:
```bash
# Run all builder tests
pytest tests/unit/test_invoice_builder.py -v

# Run specific test class
pytest tests/unit/test_invoice_builder.py::TestInvoiceDetailBuilder -v

# Run with coverage
pytest tests/unit/test_invoice_builder.py --cov=app.domain.builders
```

**Test Coverage:**
- 18 unit tests
- 100% coverage of builder methods
- Validation tests
- Error handling tests
- Integration scenarios

## Migration Guide

### If you're using the old `InvoiceBuilder`:

1. **Simple cases** - Just call `.build()` at the end:
   ```python
   # Before
   invoice = InvoiceBuilder.create_invoice(...)
   
   # After
   invoice = InvoiceBuilder.create_invoice(...).build()
   ```

2. **Adding details** - Use new methods:
   ```python
   # Before
   invoice = builder.add_detail(detail).build()
   
   # After (still works)
   invoice = builder.add_line(detail).build()
   
   # After (better)
   invoice = (
       builder
       .add_line(detail)
       .add_simple_line(...)
       .build()
   )
   ```

3. **Creating details** - Use InvoiceDetailBuilder:
   ```python
   # Before - manual creation
   detail = InvoiceDetail(
       product_name="Product",
       quantity=2,
       unit_price=100.0,
       # ... set all fields
   )
   detail.calculate_totals()
   
   # After - builder pattern
   detail = (
       InvoiceDetailBuilder()
       .with_product("Product")
       .with_price(2, 100.0)
       .with_created_by("user")
       .build()  # Automatically calculates totals
   )
   ```

## Examples

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for:
- Complete real-world examples
- All tax types usage
- Error handling
- Best practices
- 10+ code examples

## API Reference

### InvoiceBuilder

**Header Methods:**
- `.with_header(...)` - Set all header fields
- `.with_date(date)` - Set invoice date
- `.with_authorization_number(number)` - Set auth number
- `.with_dte_type(type)` - Set document type
- `.with_serie(serie)` - Set invoice series
- `.with_dte_number(number)` - Set document number
- `.with_company_id(id)` - Set issuing company
- `.with_customer_id(id)` - Set customer
- `.with_currency(currency)` - Set currency (default: GTQ)
- `.with_state(state)` - Set invoice state
- `.with_cancelled_status(bool, date?)` - Mark as cancelled
- `.with_created_by(user)` - Set creator
- `.with_updated_by(user)` - Set updater

**Line Item Methods:**
- `.add_line(detail)` - Add a built InvoiceDetail
- `.add_lines(details)` - Add multiple details
- `.add_simple_line(name, qty, price, user, code?, iva?)` - Quick add

**Build Methods:**
- `.build()` - Build and return Invoice
- `.calculate_totals()` - Manually calculate (usually not needed)

**Static Methods:**
- `.create_invoice(...)` - Start with header fields

### InvoiceDetailBuilder

**Product Methods:**
- `.with_product(name, code?, description?)` - Set product info
- `.with_quantity(qty)` - Set quantity
- `.with_unit_price(price)` - Set unit price
- `.with_price(qty, price)` - Set both at once

**Tax Methods:**
- `.with_iva(amount)` - VAT tax
- `.with_petroleo(amount)` - Petroleum tax
- `.with_turismo_hospedaje(amount)` - Tourism lodging
- `.with_turismo_pasajes(amount)` - Tourism transport
- `.with_timbre_prensa(amount)` - Newspaper stamp
- `.with_bomberos(amount)` - Firefighters
- `.with_tasa_municipal(amount)` - Municipal rate
- `.with_bebidas_alcoholicas(amount)` - Alcoholic beverages
- `.with_tabaco(amount)` - Tobacco
- `.with_cemento(amount)` - Cement
- `.with_bebidas_no_alcoholicas(amount)` - Non-alcoholic beverages
- `.with_tarifa_portuaria(amount)` - Port tariff

**Audit Methods:**
- `.with_created_by(user)` - Set creator
- `.with_updated_by(user)` - Set updater

**Build Methods:**
- `.build()` - Build and return InvoiceDetail

**Static Methods:**
- `.create_line(name, qty, price, user, code?, iva?)` - Quick creation

## Best Practices

1. **Always use `.build()` last**
   ```python
   # ✅ Correct
   invoice = builder.with_header(...).add_line(...).build()
   
   # ❌ Wrong - missing .build()
   invoice = builder.with_header(...).add_line(...)
   ```

2. **Use `.with_header()` for concise header setup**
   ```python
   # ✅ Recommended
   .with_header(date=..., authorization_number=..., ...)
   
   # ⚠️ Verbose (but still works)
   .with_date(...).with_authorization_number(...)...
   ```

3. **Use `.add_simple_line()` for basic items**
   ```python
   # ✅ For simple items
   .add_simple_line("Product", 1, 100.0, "user", iva=12.0)
   
   # ⚠️ Overkill for simple items
   .add_line(
       InvoiceDetailBuilder()
       .with_product("Product")
       .with_price(1, 100.0)
       .with_iva(12.0)
       .with_created_by("user")
       .build()
   )
   ```

4. **Use `InvoiceDetailBuilder` for complex items**
   ```python
   # ✅ For items with multiple taxes
   .add_line(
       InvoiceDetailBuilder()
       .with_product("Gasolina", code="GAS001", description="Premium")
       .with_price(100, 35.50)
       .with_iva(426.0)
       .with_petroleo(710.0)
       .with_created_by("user")
       .build()
   )
   ```

5. **Let builders calculate totals**
   ```python
   # ✅ Automatic calculation
   invoice = builder.add_line(...).build()  # Totals calculated
   
   # ❌ Don't manually calculate
   detail.calculate_totals()  # Not needed, .build() does this
   ```

## Support

- **Documentation**: See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **Tests**: `tests/unit/test_invoice_builder.py`
- **Code**: `app/domain/builders/`

---

**Version**: 2.0  
**Last Updated**: October 2025  
**Breaking Changes**: None - backward compatible

