"""
Examples of how to use the abstract BaseRepository pattern and Builder patterns
"""

from datetime import UTC, datetime

from app.domain.builders import (
    InvoiceBuilder,
    InvoiceDetailBuilder,
    VendorBuilder,
)


def vendor_examples():
    """Examples of using VendorBuilder"""

    # Example 1: Using the builder pattern step by step
    vendor_builder = VendorBuilder()
    vendor = (
        vendor_builder.with_name("Acme Corporation")
        .with_nit("12345678-9")
        .with_email("contact@acme.com")
        .with_commercial_activity("Software Development")
        .with_address("123 Main St, Guatemala City")
        .with_date_birth("1990-01-01")
        .with_created_by("admin")
        .build()
    )

    print(f"Created vendor: {vendor.name} with NIT: {vendor.nit}")

    # Example 2: Using the convenience method
    vendor2 = VendorBuilder.create_vendor(
        name="Tech Solutions Ltd",
        nit="98765432-1",
        email="info@techsolutions.com",
        created_by="system",
        commercial_activity="IT Services",
        address="456 Business Ave",
    )

    print(f"Created vendor: {vendor2.name}")

    return vendor, vendor2


def invoice_examples():
    """Examples of using InvoiceBuilder and InvoiceDetailBuilder"""

    # Example 1: Create an invoice with details
    invoice = (
        InvoiceBuilder()
        .with_date(datetime.now(UTC))
        .with_authorization_number("AUTH-2024-001")
        .with_dte_type("FACTURA")
        .with_serie("A")
        .with_dte_number("000001")
        .with_company_id(1)
        .with_customer_id(2)
        .with_currency("GTQ")
        .with_created_by("admin")
        .build()
    )

    # Create invoice details
    detail1 = (
        InvoiceDetailBuilder()
        .with_invoice_id(invoice.id or 1)
        .with_product_name("Laptop Dell XPS 13")
        .with_product_code("LAPTOP-001")
        .with_description("High-performance laptop for business")
        .with_quantity(2.0)
        .with_unit_price(15000.0)
        .with_iva(1800.0)  # 12% IVA
        .with_created_by("admin")
        .build()
    )

    detail2 = InvoiceDetailBuilder.create_detail(
        invoice_id=invoice.id or 1,
        product_name="Software License",
        quantity=1.0,
        unit_price=5000.0,
        created_by="admin",
        description="Annual software license",
        iva=600.0,
    )

    # Add details to invoice and calculate totals
    invoice.details = [detail1, detail2]
    invoice.calculate_totals()

    print(f"Invoice {invoice.dte_number} total: {invoice.total_amount}")
    print(f"Details count: {len(invoice.details)}")

    return invoice


def repository_pattern_examples():
    """Examples of how repositories would be used with the BaseRepository pattern"""

    # This is conceptual - showing how the repositories would be used
    print("Repository Pattern Examples:")
    print("===========================")

    print(
        """
    # Example 1: Using VendorRepository with BaseRepository methods
    vendor_repo = VendorRepositoryImpl(session)

    # Using base repository methods
    vendor = vendor_repo.get_by_id(1)
    all_vendors = vendor_repo.get_all(skip=0, limit=10)
    vendor_exists = vendor_repo.exists(1)

    # Using custom vendor methods
    vendor_by_email = vendor_repo.get_vendor_by_email("test@example.com")
    vendor_by_nit = vendor_repo.get_vendor_by_nit("12345678-9")
    search_results = vendor_repo.search_vendors("Acme")

    # Create using builder pattern
    new_vendor = VendorBuilder.create_vendor(
        name="New Company",
        nit="11111111-1",
        email="new@company.com",
        created_by="admin"
    )
    saved_vendor = vendor_repo.create(new_vendor)
    """
    )

    print(
        """
    # Example 2: Using InvoiceRepository with BaseRepository methods
    invoice_repo = InvoiceRepositoryImpl(session)

    # Using base repository methods
    invoice = invoice_repo.get_by_id(1)
    recent_invoices = invoice_repo.get_all(skip=0, limit=5)

    # Using custom invoice methods
    invoice_by_number = invoice_repo.get_invoice_by_number("000001", "A")
    customer_invoices = invoice_repo.get_invoices_by_customer(2)
    cancelled_invoices = invoice_repo.get_cancelled_invoices()

    # Create using builder pattern
    new_invoice = InvoiceBuilder.create_invoice(
        date=datetime.now(UTC),
        authorization_number="AUTH-2024-002",
        dte_type="FACTURA",
        serie="B",
        dte_number="000002",
        company_id=1,
        customer_id=3,
        state="DRAFT",
        created_by="user"
    )
    saved_invoice = invoice_repo.create(new_invoice)
    """
    )


if __name__ == "__main__":
    print("Domain Model Examples")
    print("====================")

    # Run vendor examples
    print("\n1. Vendor Examples:")
    vendor_examples()

    # Run invoice examples
    print("\n2. Invoice Examples:")
    invoice_examples()

    # Show repository patterns
    print("\n3. Repository Pattern Examples:")
    repository_pattern_examples()
