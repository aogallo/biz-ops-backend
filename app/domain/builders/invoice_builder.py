"""Builder pattern for creating Invoice entities."""

from datetime import UTC, datetime

from sqlmodel import SQLModel

from app.domain.builders.invoice_detail_builder import InvoiceDetailBuilder
from app.domain.entities.invoice import Invoice, InvoiceState
from app.domain.entities.invoice_detail import InvoiceDetail


class InvoiceBuilder(SQLModel):
    """Builder pattern for creating Invoice entities with line items.

    This builder follows the pure builder pattern - start with an empty builder
    and configure it step by step using the with_* methods.

    Example:
        # Pure builder pattern
        invoice = (
            InvoiceBuilder()
            .with_date(datetime.now())
            .with_authorization_number("AUTH123")
            .with_dte_type("FACTURA")
            .with_serie("A")
            .with_dte_number("001")
            .with_company_id(1)
            .with_customer_id(2)
            .with_state("draft")
            .with_created_by("user")
            .add_simple_line("Product A", 2, 100.0, "user")
            .build()
        )

        # Or use convenience classmethod
        invoice = (
            InvoiceBuilder.create_with_header(
                date=datetime.now(),
                authorization_number="AUTH123",
                dte_type="FACTURA",
                serie="A",
                dte_number="001",
                company_id=1,
                customer_id=2,
                state="draft",
                created_by="user",
            )
            .add_simple_line("Product A", 2, 100.0, "user")
            .build()
        )
    """

    def __init__(self):
        """Initialize an empty invoice builder.

        All fields will be None/default until set via builder methods.
        This follows the pure builder pattern from refactoring.guru.
        """
        self._invoice = Invoice(
            date=None,
            authorization_number=None,
            dte_type=None,
            serie=None,
            dte_number=None,
            company_id=None,
            customer_id=None,
        )
        self._invoice.created_at = datetime.now(UTC)
        self._invoice.currency = "GTQ"
        self._invoice.subtotal = 0.0
        self._invoice.total_taxes = 0.0
        self._invoice.total_amount = 0.0
        self._invoice.state = "draft"
        self._invoice.created_by = "system"
        self._invoice.updated_by = "system"
        self._invoice.updated_at = datetime.now(UTC)
        self._invoice.is_cancelled = False
        self._invoice.details = []

    # Header configuration methods
    def with_header(
        self,
        date: datetime,
        authorization_number: str,
        dte_type: str,
        serie: str,
        dte_number: str,
        company_id: int,
        customer_id: int,
        state: InvoiceState,
        created_by: str,
        currency: str = "GTQ",
    ) -> "InvoiceBuilder":
        """Set all invoice header fields at once.

        Args:
            date: Invoice date
            authorization_number: SAT authorization number
            dte_type: Document type (e.g., "FACTURA", "NOTA_CREDITO")
            serie: Invoice series
            dte_number: Document number
            company_id: Issuing company ID
            customer_id: Customer ID
            state: Invoice state (e.g., "DRAFT", "POSTED", "CANCELLED")
            created_by: Username or ID of creator
            currency: Currency code (default "GTQ")

        Returns:
            Self for method chaining
        """
        self._invoice.date = date
        self._invoice.authorization_number = authorization_number
        self._invoice.dte_type = dte_type
        self._invoice.serie = serie
        self._invoice.dte_number = dte_number
        self._invoice.company_id = company_id
        self._invoice.customer_id = customer_id
        self._invoice.state = state
        self._invoice.created_by = created_by
        self._invoice.currency = currency
        return self

    def with_date(self, date: datetime) -> "InvoiceBuilder":
        """Set invoice date.

        Args:
            date: Invoice date

        Returns:
            Self for method chaining
        """
        self._invoice.date = date
        return self

    def with_authorization_number(self, auth_number: str) -> "InvoiceBuilder":
        """Set authorization number.

        Args:
            auth_number: SAT authorization number

        Returns:
            Self for method chaining
        """
        self._invoice.authorization_number = auth_number
        return self

    def with_dte_type(self, dte_type: str) -> "InvoiceBuilder":
        """Set DTE type.

        Args:
            dte_type: Document type

        Returns:
            Self for method chaining
        """
        self._invoice.dte_type = dte_type
        return self

    def with_serie(self, serie: str) -> "InvoiceBuilder":
        """Set invoice serie.

        Args:
            serie: Invoice series

        Returns:
            Self for method chaining
        """
        self._invoice.serie = serie
        return self

    def with_dte_number(self, dte_number: str) -> "InvoiceBuilder":
        """Set DTE number.

        Args:
            dte_number: Document number

        Returns:
            Self for method chaining
        """
        self._invoice.dte_number = dte_number
        return self

    def with_company_id(self, company_id: int) -> "InvoiceBuilder":
        """Set company ID.

        Args:
            company_id: Issuing company ID

        Returns:
            Self for method chaining
        """
        self._invoice.company_id = company_id
        return self

    def with_customer_id(self, customer_id: int) -> "InvoiceBuilder":
        """Set customer ID.

        Args:
            customer_id: Customer ID

        Returns:
            Self for method chaining
        """
        self._invoice.customer_id = customer_id
        return self

    def with_currency(self, currency: str) -> "InvoiceBuilder":
        """Set invoice currency.

        Args:
            currency: Currency code (e.g., "GTQ", "USD")

        Returns:
            Self for method chaining
        """
        self._invoice.currency = currency
        return self

    def with_state(self, state: InvoiceState) -> "InvoiceBuilder":
        """Set invoice state.

        Args:
            state: Invoice state

        Returns:
            Self for method chaining
        """
        self._invoice.state = state
        return self

    def with_cancelled_status(
        self, is_cancelled: bool, cancelled_date: datetime | None = None
    ) -> "InvoiceBuilder":
        """Set cancelled status.

        Args:
            is_cancelled: Whether invoice is cancelled
            cancelled_date: Optional cancellation date

        Returns:
            Self for method chaining
        """
        self._invoice.is_cancelled = is_cancelled
        if is_cancelled and cancelled_date:
            self._invoice.cancelled_date = cancelled_date
        return self

    def with_created_by(self, created_by: str) -> "InvoiceBuilder":
        """Set who created the invoice.

        Args:
            created_by: Username or ID of creator

        Returns:
            Self for method chaining
        """
        self._invoice.created_by = created_by
        return self

    def with_updated_by(self, updated_by: str) -> "InvoiceBuilder":
        """Set who updated the invoice.

        Args:
            updated_by: Username or ID of updater

        Returns:
            Self for method chaining
        """
        self._invoice.updated_by = updated_by
        self._invoice.updated_at = datetime.now(UTC)
        return self

    # Line item methods
    def add_line(self, detail: InvoiceDetail) -> "InvoiceBuilder":
        """Add a single invoice line item.

        Args:
            detail: Built InvoiceDetail instance

        Returns:
            Self for method chaining

        Example:
            .add_line(
                InvoiceDetailBuilder()
                .with_product("Product A")
                .with_price(2, 100.0)
                .with_created_by("user")
                .build()
            )
        """
        self._invoice.details.append(detail)
        return self

    def add_lines(self, details: list[InvoiceDetail]) -> "InvoiceBuilder":
        """Add multiple invoice line items.

        Args:
            details: List of InvoiceDetail instances

        Returns:
            Self for method chaining
        """
        self._invoice.details.extend(details)
        return self

    def add_simple_line(
        self,
        product_name: str,
        quantity: float,
        unit_price: float,
        created_by: str,
        product_code: str | None = None,
        iva: float = 0.0,
    ) -> "InvoiceBuilder":
        """Add a simple line item without using a builder.

        Args:
            product_name: Product name
            quantity: Item quantity
            unit_price: Price per unit
            created_by: Username or ID of creator
            product_code: Optional product code
            iva: IVA (VAT) amount (default 0.0)

        Returns:
            Self for method chaining

        Example:
            .add_simple_line("Product A", 2, 100.0, "user", iva=24.0)
        """
        detail = InvoiceDetailBuilder.create_line(
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            created_by=created_by,
            product_code=product_code,
            iva=iva,
        )
        return self.add_line(detail)

    def calculate_totals(self) -> "InvoiceBuilder":
        """Calculate invoice totals from details.

        Returns:
            Self for method chaining
        """
        self._invoice.calculate_totals()
        return self

    def build(self) -> Invoice:
        """Build and return the invoice instance.

        Returns:
            Configured Invoice instance

        Raises:
            ValueError: If required fields are missing
        """
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
    def create_with_header(
        cls,
        date: datetime,
        authorization_number: str,
        dte_type: str,
        serie: str,
        dte_number: str,
        company_id: int,
        customer_id: int,
        state: InvoiceState,
        created_by: str,
        currency: str = "GTQ",
    ) -> "InvoiceBuilder":
        """Convenience classmethod to create a builder with all header fields.

        This is a convenience method that sets all required header fields at once.
        Returns a builder instance ready to add line items and build.

        Args:
            date: Invoice date
            authorization_number: SAT authorization number
            dte_type: Document type (e.g., "FACTURA", "NOTA_CREDITO")
            serie: Invoice series
            dte_number: Document number
            company_id: Issuing company ID
            customer_id: Customer ID
            state: Invoice state (e.g., "draft", "open", "paid", "void")
            created_by: Username or ID of creator
            currency: Currency code (default "GTQ")

        Returns:
            InvoiceBuilder instance with header set, ready to add line items

        Example:
            invoice = (
                InvoiceBuilder.create_with_header(
                    date=datetime.now(),
                    authorization_number="AUTH123",
                    dte_type="FACTURA",
                    serie="A",
                    dte_number="001",
                    company_id=1,
                    customer_id=2,
                    state="draft",
                    created_by="user",
                )
                .add_simple_line("Product A", 2, 100.0, "user", iva=24.0)
                .build()
            )
        """
        return cls().with_header(
            date=date,
            authorization_number=authorization_number,
            dte_type=dte_type,
            serie=serie,
            dte_number=dte_number,
            company_id=company_id,
            customer_id=customer_id,
            state=state,
            created_by=created_by,
            currency=currency,
        )

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
        state: InvoiceState,
        created_by: str,
        currency: str = "GTQ",
    ) -> "InvoiceBuilder":
        """Convenience method to create an invoice builder with header fields.

        This is an alias for create_with_header() for backward compatibility.

        This returns a builder instance, not a built invoice, so you can
        continue adding line items.

        Args:
            date: Invoice date
            authorization_number: SAT authorization number
            dte_type: Document type
            serie: Invoice series
            dte_number: Document number
            company_id: Issuing company ID
            customer_id: Customer ID
            state: Invoice state
            created_by: Username or ID of creator
            currency: Currency code (default "GTQ")

        Returns:
            InvoiceBuilder instance ready to add line items

        Example:
            invoice = (
                InvoiceBuilder.create_invoice(...)
                .add_simple_line("Product A", 2, 100.0, "user", iva=24.0)
                .build()
            )
        """
        return cls.create_with_header(
            date=date,
            authorization_number=authorization_number,
            dte_type=dte_type,
            serie=serie,
            dte_number=dte_number,
            company_id=company_id,
            customer_id=customer_id,
            state=state,
            created_by=created_by,
            currency=currency,
        )
