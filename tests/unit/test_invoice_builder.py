"""Unit tests for InvoiceBuilder and InvoiceDetailBuilder."""

from datetime import datetime

import pytest

from app.domain.builders.invoice_builder import InvoiceBuilder
from app.domain.builders.invoice_detail_builder import InvoiceDetailBuilder


class TestInvoiceDetailBuilder:
    """Test InvoiceDetailBuilder."""

    def test_create_simple_detail(self):
        """Test creating a simple invoice detail."""
        detail = (
            InvoiceDetailBuilder()
            .with_product("Product A", code="PRD001")
            .with_price(quantity=2, unit_price=100.0)
            .with_iva(24.0)
            .with_created_by("test_user")
            .build()
        )

        assert detail.product_name == "Product A"
        assert detail.product_code == "PRD001"
        assert detail.quantity == 2
        assert detail.unit_price == 100.0
        assert detail.iva == 24.0
        assert detail.subtotal == 200.0  # 2 * 100
        assert detail.total_taxes == 24.0
        assert detail.total == 224.0  # 200 + 24

    def test_create_detail_with_multiple_taxes(self):
        """Test creating detail with multiple taxes."""
        detail = (
            InvoiceDetailBuilder()
            .with_product("Gasoline")
            .with_price(quantity=100, unit_price=35.5)
            .with_iva(426.0)
            .with_petroleo(710.0)
            .with_created_by("test_user")
            .build()
        )

        assert detail.subtotal == 3550.0  # 100 * 35.5
        assert detail.total_taxes == 1136.0  # 426 + 710
        assert detail.total == 4686.0

    def test_create_line_convenience_method(self):
        """Test InvoiceDetailBuilder.create_line() convenience method."""
        detail = InvoiceDetailBuilder.create_line(
            product_name="Product B",
            quantity=5,
            unit_price=50.0,
            created_by="test_user",
            product_code="PRD002",
            iva=30.0,
        )

        assert detail.product_name == "Product B"
        assert detail.product_code == "PRD002"
        assert detail.quantity == 5
        assert detail.unit_price == 50.0
        assert detail.subtotal == 250.0
        assert detail.iva == 30.0
        assert detail.total == 280.0

    def test_detail_missing_required_fields(self):
        """Test that missing required fields raise ValueError."""
        with pytest.raises(ValueError, match="Product name is required"):
            InvoiceDetailBuilder().with_price(1, 100.0).with_created_by(
                "test"
            ).build()

        with pytest.raises(ValueError, match="Quantity is required"):
            (
                InvoiceDetailBuilder()
                .with_product("Product")
                .with_unit_price(100.0)
                .with_created_by("test")
                .build()
            )

        with pytest.raises(ValueError, match="Created by is required"):
            (
                InvoiceDetailBuilder()
                .with_product("Product")
                .with_price(1, 100.0)
                .build()
            )

    def test_detail_invalid_quantity(self):
        """Test that invalid quantity raises ValueError."""
        with pytest.raises(
            ValueError, match="Quantity must be greater than 0"
        ):
            (
                InvoiceDetailBuilder()
                .with_product("Product")
                .with_quantity(-5)
                .with_unit_price(100.0)
                .with_created_by("test")
                .build()
            )

    def test_detail_invalid_unit_price(self):
        """Test that negative unit price raises ValueError."""
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            (
                InvoiceDetailBuilder()
                .with_product("Product")
                .with_quantity(1)
                .with_unit_price(-100.0)
                .with_created_by("test")
                .build()
            )


class TestInvoiceBuilder:
    """Test InvoiceBuilder."""

    def test_create_invoice_with_header(self):
        """Test creating invoice using with_header()."""
        invoice = (
            InvoiceBuilder()
            .with_header(
                date=datetime(2025, 10, 15),
                authorization_number="AUTH123",
                dte_type="FACTURA",
                serie="A",
                dte_number="001",
                company_id=1,
                customer_id=2,
                state="draft",
                created_by="test_user",
                currency="GTQ",
            )
            .build()
        )

        assert invoice.date == datetime(2025, 10, 15)
        assert invoice.authorization_number == "AUTH123"
        assert invoice.dte_type == "FACTURA"
        assert invoice.serie == "A"
        assert invoice.dte_number == "001"
        assert invoice.company_id == 1
        assert invoice.customer_id == 2
        assert invoice.state == "draft"
        assert invoice.currency == "GTQ"
        assert invoice.created_by == "test_user"

    def test_create_invoice_with_line_items(self):
        """Test creating invoice with line items."""
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
                state="draft",
                created_by="test_user",
            )
            .add_line(
                InvoiceDetailBuilder()
                .with_product("Product A")
                .with_price(2, 100.0)
                .with_iva(24.0)
                .with_created_by("test_user")
                .build()
            )
            .add_line(
                InvoiceDetailBuilder()
                .with_product("Product B")
                .with_price(1, 200.0)
                .with_iva(24.0)
                .with_created_by("test_user")
                .build()
            )
            .build()
        )

        assert len(invoice.details) == 2
        assert invoice.subtotal == 400.0  # (2*100) + (1*200)
        assert invoice.total_taxes == 48.0  # 24 + 24
        assert invoice.total_amount == 448.0  # 400 + 48

    def test_create_invoice_with_simple_lines(self):
        """Test creating invoice using add_simple_line()."""
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
                state="draft",
                created_by="test_user",
            )
            .add_simple_line("Product A", 2, 100.0, "test_user", iva=24.0)
            .add_simple_line("Product B", 1, 200.0, "test_user", iva=24.0)
            .build()
        )

        assert len(invoice.details) == 2
        assert invoice.subtotal == 400.0
        assert invoice.total_taxes == 48.0
        assert invoice.total_amount == 448.0

    def test_create_invoice_convenience_method(self):
        """Test InvoiceBuilder.create_invoice() convenience method."""
        invoice = (
            InvoiceBuilder.create_invoice(
                date=datetime.now(),
                authorization_number="AUTH123",
                dte_type="FACTURA",
                serie="A",
                dte_number="001",
                company_id=1,
                customer_id=2,
                state="draft",
                created_by="test_user",
            )
            .add_simple_line("Product A", 1, 100.0, "test_user")
            .build()
        )

        assert invoice.authorization_number == "AUTH123"
        assert len(invoice.details) == 1

    def test_add_multiple_lines_at_once(self):
        """Test adding multiple line items at once."""
        details = [
            InvoiceDetailBuilder.create_line(
                "Product A", 2, 100.0, "test_user"
            ),
            InvoiceDetailBuilder.create_line(
                "Product B", 1, 200.0, "test_user"
            ),
            InvoiceDetailBuilder.create_line(
                "Product C", 5, 50.0, "test_user"
            ),
        ]

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
                state="draft",
                created_by="test_user",
            )
            .add_lines(details)
            .build()
        )

        assert len(invoice.details) == 3
        assert invoice.subtotal == 650.0  # (2*100) + (1*200) + (5*50)

    def test_invoice_missing_required_fields(self):
        """Test that missing required fields raise ValueError."""
        # Test missing date
        with pytest.raises(ValueError, match="Invoice date is required"):
            InvoiceBuilder().build()

        # Test missing authorization_number
        with pytest.raises(
            ValueError, match="Authorization number is required"
        ):
            InvoiceBuilder().with_date(datetime.now()).build()

        # Test missing dte_type
        with pytest.raises(ValueError, match="DTE type is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .build()
            )

        # Test missing serie
        with pytest.raises(ValueError, match="Invoice serie is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .build()
            )

        # Test missing dte_number
        with pytest.raises(ValueError, match="DTE number is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .with_serie("A")
                .build()
            )

        # Test missing company_id
        with pytest.raises(ValueError, match="Company ID is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .with_serie("A")
                .with_dte_number("001")
                .build()
            )

        # Test missing customer_id
        with pytest.raises(ValueError, match="Customer ID is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .with_serie("A")
                .with_dte_number("001")
                .with_company_id(1)
                .build()
            )

        # Test missing state
        with pytest.raises(ValueError, match="Invoice state is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .with_serie("A")
                .with_dte_number("001")
                .with_company_id(1)
                .with_customer_id(2)
                .build()
            )

        # Test missing created_by
        with pytest.raises(ValueError, match="Created by is required"):
            (
                InvoiceBuilder()
                .with_date(datetime.now())
                .with_authorization_number("AUTH123")
                .with_dte_type("FACTURA")
                .with_serie("A")
                .with_dte_number("001")
                .with_company_id(1)
                .with_customer_id(2)
                .with_state("draft")
                .build()
            )

    def test_invoice_with_cancelled_status(self):
        """Test setting cancelled status."""
        cancelled_date = datetime.now()
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
                state="void",
                created_by="test_user",
            )
            .with_cancelled_status(True, cancelled_date)
            .build()
        )

        assert invoice.is_cancelled is True
        assert invoice.cancelled_date == cancelled_date

    def test_invoice_totals_calculated_automatically(self):
        """Test that totals are calculated automatically on build()."""
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
                state="draft",
                created_by="test_user",
            )
            .add_simple_line("Product A", 10, 100.0, "test_user", iva=120.0)
            .add_simple_line("Product B", 5, 200.0, "test_user", iva=120.0)
            .build()
        )

        # Totals should be calculated automatically
        assert invoice.subtotal == 2000.0  # (10*100) + (5*200)
        assert invoice.total_taxes == 240.0  # 120 + 120
        assert invoice.total_amount == 2240.0  # 2000 + 240

    def test_invoice_with_updated_by(self):
        """Test setting updated_by field."""
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
                state="draft",
                created_by="test_user",
            )
            .with_updated_by("admin_user")
            .build()
        )

        assert invoice.updated_by == "admin_user"
        assert invoice.updated_at is not None

    def test_create_with_header_convenience_method(self):
        """Test InvoiceBuilder.create_with_header() convenience method."""
        invoice = (
            InvoiceBuilder.create_with_header(
                date=datetime.now(),
                authorization_number="AUTH456",
                dte_type="NOTA_CREDITO",
                serie="B",
                dte_number="002",
                company_id=1,
                customer_id=3,
                state="draft",
                created_by="test_user",
                currency="USD",
            )
            .add_simple_line("Product X", 3, 75.0, "test_user", iva=27.0)
            .build()
        )

        assert invoice.authorization_number == "AUTH456"
        assert invoice.dte_type == "NOTA_CREDITO"
        assert invoice.serie == "B"
        assert invoice.dte_number == "002"
        assert invoice.currency == "USD"
        assert len(invoice.details) == 1
        assert invoice.subtotal == 225.0  # 3 * 75

    def test_pure_builder_pattern(self):
        """Test using pure builder pattern step by step."""
        invoice = (
            InvoiceBuilder()
            .with_date(datetime.now())
            .with_authorization_number("AUTH789")
            .with_dte_type("FACTURA")
            .with_serie("C")
            .with_dte_number("003")
            .with_company_id(2)
            .with_customer_id(4)
            .with_state("draft")
            .with_created_by("builder_user")
            .with_currency("EUR")
            .add_simple_line("Service A", 1, 500.0, "builder_user", iva=60.0)
            .build()
        )

        assert invoice.authorization_number == "AUTH789"
        assert invoice.currency == "EUR"
        assert invoice.company_id == 2
        assert invoice.customer_id == 4
        assert invoice.created_by == "builder_user"
        assert len(invoice.details) == 1
