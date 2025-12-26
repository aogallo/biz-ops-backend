"""Unit tests for invoice classification enums and validation."""

from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.internal.invoice.entity import (
    Invoice,
    InvoiceCreate,
    InvoiceItemType,
    InvoiceOrigin,
    InvoiceTaxStatus,
)
from app.internal.invoice.schema import (
    InvoiceCreate as InvoiceCreateSchema,
)
from app.internal.invoice.schema import (
    InvoiceResponse,
    InvoiceUpdate,
)
from app.internal.invoice.service import InvoiceService
from app.internal.user.entity import UserAuthenticated


class TestInvoiceClassificationEnums:
    """Test invoice classification enum definitions."""

    def test_invoice_origin_values(self):
        """Test InvoiceOrigin enum has correct values."""
        assert InvoiceOrigin.LOCAL == "local"
        assert InvoiceOrigin.IMPORTED == "imported"
        assert len(list(InvoiceOrigin)) == 2

    def test_invoice_item_type_values(self):
        """Test InvoiceItemType enum has correct values."""
        assert InvoiceItemType.GOODS == "goods"
        assert InvoiceItemType.SERVICES == "services"
        assert len(list(InvoiceItemType)) == 2

    def test_invoice_tax_status_values(self):
        """Test InvoiceTaxStatus enum has correct values."""
        assert InvoiceTaxStatus.TAXED == "taxed"
        assert InvoiceTaxStatus.EXEMPT == "exempt"
        assert len(list(InvoiceTaxStatus)) == 2


class TestInvoiceEntityClassification:
    """Test Invoice entity with classification fields."""

    def test_invoice_create_with_null_classification(self):
        """Test InvoiceCreate defaults to NULL classification values."""
        invoice_data = InvoiceCreate(
            date=datetime.now(),
            authorization_number="123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
        )
        # Should have NULL defaults
        assert invoice_data.origin is None
        assert invoice_data.item_type is None
        assert invoice_data.tax_status is None

    def test_invoice_create_with_explicit_classification(self):
        """Test creating invoice with explicit classification."""
        invoice_data = InvoiceCreate(
            date=datetime.now(),
            authorization_number="123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            origin="imported",
            item_type="services",
            tax_status="exempt",
        )
        assert invoice_data.origin == "imported"
        assert invoice_data.item_type == "services"
        assert invoice_data.tax_status == "exempt"

    def test_invoice_create_with_partial_classification(self):
        """Test creating invoice with partial classification (some NULL)."""
        invoice_data = InvoiceCreate(
            date=datetime.now(),
            authorization_number="123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            origin="local",
            # item_type and tax_status not provided (NULL)
        )
        assert invoice_data.origin == "local"
        assert invoice_data.item_type is None
        assert invoice_data.tax_status is None

    def test_all_eight_classification_combinations(self):
        """Test all 8 valid classification combinations can be created."""
        combinations = [
            ("local", "goods", "taxed"),  # locally_taxed_goods
            ("local", "services", "taxed"),  # locally_taxed_services
            ("local", "goods", "exempt"),  # locally_exempt_goods
            ("local", "services", "exempt"),  # locally_exempt_services
            ("imported", "goods", "taxed"),  # imported_taxed_goods
            ("imported", "services", "taxed"),  # imported_taxed_services
            ("imported", "goods", "exempt"),  # imported_exempt_goods
            ("imported", "services", "exempt"),  # imported_exempt_services
        ]

        for origin, item_type, tax_status in combinations:
            invoice = InvoiceCreate(
                date=datetime.now(),
                authorization_number="123",
                dte_type="FACT",
                serie="A",
                dte_number="100",
                company_id=1,
                customer_id=1,
                origin=origin,
                item_type=item_type,
                tax_status=tax_status,
            )
            assert invoice.origin == origin
            assert invoice.item_type == item_type
            assert invoice.tax_status == tax_status


class TestInvoiceSchemaClassification:
    """Test invoice API schemas with classification."""

    def test_invoice_create_schema_accepts_null_classification(self):
        """Test InvoiceCreate schema accepts NULL classification (optional)."""
        schema = InvoiceCreateSchema(
            date=datetime.now(),
            authorization_number="AUTH123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            # Classification fields not provided
        )
        # Should have None values
        assert schema.origin is None
        assert schema.item_type is None
        assert schema.tax_status is None

    def test_invoice_create_schema_accepts_classification(self):
        """Test InvoiceCreate schema accepts classification fields."""
        schema = InvoiceCreateSchema(
            date=datetime.now(),
            authorization_number="AUTH123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            origin="imported",
            item_type="services",
            tax_status="exempt",
        )
        assert schema.origin == "imported"
        assert schema.item_type == "services"
        assert schema.tax_status == "exempt"

    def test_invoice_response_schema_serializes_camelcase(self):
        """Test InvoiceResponse uses camelCase serialization."""
        # Create entity
        invoice = Invoice(
            id=1,
            date=datetime.now(),
            authorization_number="AUTH123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            currency="GTQ",
            subtotal=100.0,
            total_taxes=12.0,
            total_amount=112.0,
            state="draft",
            invoice_type="incomes",
            origin="imported",
            item_type="services",
            tax_status="exempt",
            created_by="user123",
            created_at=datetime.now(),
        )

        # Convert to response schema
        response = InvoiceResponse.model_validate(invoice)

        # Serialize to dict (triggers serialization_alias)
        data = response.model_dump(by_alias=True)

        # Check camelCase keys exist
        assert "origin" in data
        assert "itemType" in data
        assert "taxStatus" in data
        assert data["origin"] == "imported"
        assert data["itemType"] == "services"
        assert data["taxStatus"] == "exempt"

    def test_invoice_response_schema_handles_null_classification(self):
        """Test InvoiceResponse handles NULL classification values."""
        invoice = Invoice(
            id=1,
            date=datetime.now(),
            authorization_number="AUTH123",
            dte_type="FACT",
            serie="A",
            dte_number="100",
            company_id=1,
            customer_id=1,
            currency="GTQ",
            subtotal=100.0,
            total_taxes=0.0,
            total_amount=100.0,
            state="draft",
            invoice_type="incomes",
            origin=None,  # Not classified
            item_type=None,
            tax_status=None,
            created_by="user123",
            created_at=datetime.now(),
        )

        response = InvoiceResponse.model_validate(invoice)
        data = response.model_dump(by_alias=True)

        assert data["origin"] is None
        assert data["itemType"] is None
        assert data["taxStatus"] is None

    def test_invoice_update_schema_optional_classification(self):
        """Test InvoiceUpdate allows optional classification updates."""
        schema = InvoiceUpdate(
            origin="local",
            item_type="goods",
        )
        assert schema.origin == "local"
        assert schema.item_type == "goods"
        assert schema.tax_status is None  # Not updated


class TestInvoiceServiceClassificationValidation:
    """Test invoice service validates classification fields."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return UserAuthenticated(auth_id="auth0|test", permissions=[])

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session, mock_user):
        """Create invoice service."""
        return InvoiceService(session=mock_session, current_user=mock_user)

    def test_validate_classification_field_accepts_none(self, service):
        """Test validation accepts None values (no validation when NULL)."""
        # Should not raise exception for None
        service._validate_classification_field("origin", None, InvoiceOrigin)
        service._validate_classification_field(
            "item_type", None, InvoiceItemType
        )
        service._validate_classification_field(
            "tax_status", None, InvoiceTaxStatus
        )

    def test_validate_classification_field_accepts_valid_origin(self, service):
        """Test validation accepts valid origin values."""
        service._validate_classification_field(
            "origin", "local", InvoiceOrigin
        )
        service._validate_classification_field(
            "origin", "imported", InvoiceOrigin
        )

    def test_validate_classification_field_rejects_invalid_origin(
        self, service
    ):
        """Test validation rejects invalid origin values."""
        with pytest.raises(HTTPException) as exc:
            service._validate_classification_field(
                "origin", "invalid", InvoiceOrigin
            )
        assert exc.value.status_code == 400
        assert "origin" in str(exc.value.detail).lower()

    def test_validate_classification_field_accepts_valid_item_type(
        self, service
    ):
        """Test validation accepts valid item_type values."""
        service._validate_classification_field(
            "item_type", "goods", InvoiceItemType
        )
        service._validate_classification_field(
            "item_type", "services", InvoiceItemType
        )

    def test_validate_classification_field_rejects_invalid_item_type(
        self, service
    ):
        """Test validation rejects invalid item_type values."""
        with pytest.raises(HTTPException) as exc:
            service._validate_classification_field(
                "item_type", "unknown", InvoiceItemType
            )
        assert exc.value.status_code == 400
        assert "item_type" in str(exc.value.detail).lower()

    def test_validate_classification_field_accepts_valid_tax_status(
        self, service
    ):
        """Test validation accepts valid tax_status values."""
        service._validate_classification_field(
            "tax_status", "taxed", InvoiceTaxStatus
        )
        service._validate_classification_field(
            "tax_status", "exempt", InvoiceTaxStatus
        )

    def test_validate_classification_field_rejects_invalid_tax_status(
        self, service
    ):
        """Test validation rejects invalid tax_status values."""
        with pytest.raises(HTTPException) as exc:
            service._validate_classification_field(
                "tax_status", "maybe", InvoiceTaxStatus
            )
        assert exc.value.status_code == 400
        assert "tax_status" in str(exc.value.detail).lower()
