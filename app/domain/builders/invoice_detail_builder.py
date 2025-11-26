"""Builder pattern for creating InvoiceDetail entities."""

from datetime import UTC, datetime

from app.domain.entities.invoice_detail import InvoiceDetail


class InvoiceDetailBuilder:
    """Builder pattern for creating InvoiceDetail line items.

    This builder follows the pure builder pattern - start with an empty builder
    and configure it step by step using the with_* methods.

    Example:
        detail = (
            InvoiceDetailBuilder()
            .with_product("Product A", code="PRD001")
            .with_price(quantity=2, unit_price=100.0)
            .with_iva(24.0)
            .with_created_by("test_user")
            .build()
        )
    """

    def __init__(self, invoice_id: int | None = None):
        """Initialize an empty invoice detail builder.

        All fields will be None/default until set via builder methods.
        This follows the pure builder pattern from refactoring.guru.

        Args:
            invoice_id: Optional invoice ID (can be set later, defaults to 0)
        """
        self._detail = InvoiceDetail(
            invoice_id=invoice_id,
            product_name="",
            quantity=0.0,
            unit_price=0.0,
            created_by="",
        )

        # Set tax defaults to 0.0
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

        # Set calculated defaults
        self._detail.subtotal = 0.0
        self._detail.total_taxes = 0.0
        self._detail.total = 0.0

    def with_product(
        self,
        name: str,
        code: str | None = None,
        description: str | None = None,
    ) -> "InvoiceDetailBuilder":
        """Set product information.

        Args:
            name: Product name (required)
            code: Product code (optional)
            description: Product description (optional)
        """
        self._detail.product_name = name
        if code:
            self._detail.product_code = code
        if description:
            self._detail.description = description
        return self

    def with_quantity(self, quantity: float) -> "InvoiceDetailBuilder":
        """Set quantity.

        Args:
            quantity: Item quantity
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        self._detail.quantity = quantity
        return self

    def with_unit_price(self, unit_price: float) -> "InvoiceDetailBuilder":
        """Set unit price.

        Args:
            unit_price: Price per unit
        """
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        self._detail.unit_price = unit_price
        return self

    def with_price(
        self, quantity: float, unit_price: float
    ) -> "InvoiceDetailBuilder":
        """Set both quantity and unit price in one call.

        Args:
            quantity: Item quantity
            unit_price: Price per unit
        """
        return self.with_quantity(quantity).with_unit_price(unit_price)

    # Tax setters
    def with_iva(self, amount: float) -> "InvoiceDetailBuilder":
        """Set IVA (VAT) tax amount."""
        self._detail.iva = amount
        return self

    def with_petroleo(self, amount: float) -> "InvoiceDetailBuilder":
        """Set petroleum tax amount."""
        self._detail.petroleo = amount
        return self

    def with_turismo_hospedaje(self, amount: float) -> "InvoiceDetailBuilder":
        """Set tourism lodging tax amount."""
        self._detail.turismo_hospedaje = amount
        return self

    def with_turismo_pasajes(self, amount: float) -> "InvoiceDetailBuilder":
        """Set tourism transport tax amount."""
        self._detail.turismo_pasajes = amount
        return self

    def with_timbre_prensa(self, amount: float) -> "InvoiceDetailBuilder":
        """Set newspaper stamp tax amount."""
        self._detail.timbre_prensa = amount
        return self

    def with_bomberos(self, amount: float) -> "InvoiceDetailBuilder":
        """Set firefighters tax amount."""
        self._detail.bomberos = amount
        return self

    def with_tasa_municipal(self, amount: float) -> "InvoiceDetailBuilder":
        """Set municipal rate amount."""
        self._detail.tasa_municipal = amount
        return self

    def with_bebidas_alcoholicas(
        self, amount: float
    ) -> "InvoiceDetailBuilder":
        """Set alcoholic beverages tax amount."""
        self._detail.bebidas_alcoholicas = amount
        return self

    def with_tabaco(self, amount: float) -> "InvoiceDetailBuilder":
        """Set tobacco tax amount."""
        self._detail.tabaco = amount
        return self

    def with_cemento(self, amount: float) -> "InvoiceDetailBuilder":
        """Set cement tax amount."""
        self._detail.cemento = amount
        return self

    def with_bebidas_no_alcoholicas(
        self, amount: float
    ) -> "InvoiceDetailBuilder":
        """Set non-alcoholic beverages tax amount."""
        self._detail.bebidas_no_alcoholicas = amount
        return self

    def with_tarifa_portuaria(self, amount: float) -> "InvoiceDetailBuilder":
        """Set port tariff amount."""
        self._detail.tarifa_portuaria = amount
        return self

    def with_created_by(self, created_by: str) -> "InvoiceDetailBuilder":
        """Set who created the detail.

        Args:
            created_by: Username or ID of creator
        """
        self._detail.created_by = created_by
        return self

    def with_updated_by(self, updated_by: str) -> "InvoiceDetailBuilder":
        """Set who updated the detail.

        Args:
            updated_by: Username or ID of updater
        """
        self._detail.updated_by = updated_by
        self._detail.updated_at = datetime.now(UTC)
        return self

    def build(self) -> InvoiceDetail:
        """Build and return the invoice detail.

        Returns:
            Configured InvoiceDetail instance

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not self._detail.product_name:
            raise ValueError("Product name is required")
        if self._detail.quantity is None or self._detail.quantity <= 0:
            raise ValueError("Quantity is required and must be greater than 0")
        if self._detail.unit_price is None or self._detail.unit_price < 0:
            raise ValueError("Unit price is required and cannot be negative")
        if not self._detail.created_by:
            raise ValueError("Created by is required")

        # Calculate totals
        self._detail.calculate_totals()

        return self._detail

    @classmethod
    def create_line(
        cls,
        product_name: str,
        quantity: float,
        unit_price: float,
        created_by: str,
        product_code: str | None = None,
        iva: float = 0.0,
    ) -> InvoiceDetail:
        """Convenience method to create a simple invoice line.

        Args:
            product_name: Product name
            quantity: Item quantity
            unit_price: Price per unit
            created_by: Username or ID of creator
            product_code: Optional product code
            iva: IVA (VAT) amount (default 0.0)

        Returns:
            Configured InvoiceDetail instance
        """
        builder = (
            cls()
            .with_product(product_name, code=product_code)
            .with_price(quantity, unit_price)
            .with_created_by(created_by)
        )

        if iva > 0:
            builder = builder.with_iva(iva)

        return builder.build()
