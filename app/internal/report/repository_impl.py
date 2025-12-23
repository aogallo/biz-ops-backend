"""Implementation of report repository."""

from datetime import datetime

from sqlmodel import Session, col, select

from app.internal.account.entity import Account
from app.internal.customer.entity import Customer
from app.internal.invoice.entity import Invoice, InvoiceDetail
from app.internal.journal.entity import JournalEntry
from app.internal.report.repository import ReportRepository
from app.internal.report.schemas import (
    GeneralJournalEntry,
    SalesLedgerEntry,
)


class ReportRepositoryImpl(ReportRepository):
    """Implementation of Report Repository."""

    def __init__(self, session: Session) -> None:
        self.db = session

    def get_general_journal_entries(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[GeneralJournalEntry]:
        """Get general journal entries for a company within a date range."""
        # Build query joining JournalEntry with Account and Invoice
        statement = (
            select(  # type: ignore
                col(Invoice.date),
                col(Account.account_number),
                col(Account.name),
                col(JournalEntry.description),
                col(JournalEntry.debit),
                col(JournalEntry.credit),
                col(Invoice.id),
            )
            .join(Account, JournalEntry.account_id == Account.id)
            .join(Invoice, JournalEntry.invoice_id == Invoice.id)
            .where(JournalEntry.company_id == company_id)
            .order_by(Invoice.date, Invoice.id)
        )

        # Add date filters if provided
        if start_date:
            statement = statement.where(Invoice.date >= start_date)
        if end_date:
            statement = statement.where(Invoice.date <= end_date)

        results = self.db.exec(statement).all()

        # Map results to GeneralJournalEntry schema
        entries = [
            GeneralJournalEntry(
                date=row[0],
                account_number=row[1],
                account_name=row[2],
                transaction_concept=row[3],
                debit=row[4],
                credit=row[5],
                folio_number=row[6],
            )
            for row in results
        ]

        return entries

    def get_sales_ledger_entries(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[SalesLedgerEntry]:
        """Get sales ledger entries for a company within a date range."""

        statement = (
            select(  # type: ignore
                col(Invoice.date),
                col(Invoice.dte_type),
                col(Invoice.serie),
                col(Invoice.dte_number),
                col(Customer.nit),
                col(Customer.name),
                col(Invoice.subtotal),
                col(InvoiceDetail.iva),
                col(Invoice.total_amount),
                col(Invoice.origin),
                col(Invoice.item_type),
                col(Invoice.tax_status),
            )
            .join(Customer, Customer.id == Invoice.customer_id)
            .join(InvoiceDetail, InvoiceDetail.invoice_id == Invoice.id)
            .where(
                Invoice.company_id == company_id,
                Invoice.invoice_type == "incomes",
            )
            .order_by(Invoice.date, Invoice.id)
        )

        # Add date filters if provided
        if start_date:
            statement = statement.where(Invoice.date >= start_date)
        if end_date:
            statement = statement.where(Invoice.date <= end_date)

        invoices = self.db.exec(statement).all()

        # Classification mapping dictionary
        classification_map = {
            ("local", "goods", "taxed"): "locally_taxed_goods",
            ("local", "services", "taxed"): "locally_taxed_services",
            ("local", "goods", "exempt"): "locally_exempt_goods",
            ("local", "services", "exempt"): "locally_exempt_services",
            ("imported", "goods", "taxed"): "imported_taxed_goods",
            ("imported", "services", "taxed"): "imported_taxed_services",
            ("imported", "goods", "exempt"): "imported_exempt_goods",
            ("imported", "services", "exempt"): "imported_exempt_services",
        }

        entries = []
        for row in invoices:
            # Extract classification fields (row[9], row[10], row[11])
            origin, item_type, tax_status = row[9], row[10], row[11]

            # Initialize all categories to 0.0
            amounts = {
                "locally_taxed_goods": 0.0,
                "locally_taxed_services": 0.0,
                "locally_exempt_goods": 0.0,
                "locally_exempt_services": 0.0,
                "imported_taxed_goods": 0.0,
                "imported_taxed_services": 0.0,
                "imported_exempt_goods": 0.0,
                "imported_exempt_services": 0.0,
            }

            # Only populate if ALL three fields are non-NULL
            if (
                origin is not None
                and item_type is not None
                and tax_status is not None
            ):
                classification_key = (origin, item_type, tax_status)
                if classification_key in classification_map:
                    category = classification_map[classification_key]
                    amounts[category] = row[6]  # subtotal

            entry = SalesLedgerEntry(
                date=row[0],
                type=row[1],
                transaction_type="L",
                serie=row[2],
                number_doc=row[3],
                nit=row[4],
                name=row[5],
                **amounts,  # Unpack the amounts dictionary
                iva=row[7],
                total=row[8],
            )
            entries.append(entry)

        return entries
