"""Implementation of report repository."""
from datetime import datetime

from sqlmodel import Session, col, select

from app.internal.account.entity import Account
from app.internal.invoice.entity import Invoice
from app.internal.journal.entity import JournalEntry
from app.internal.report.repository import ReportRepository
from app.internal.report.schemas import GeneralJournalEntry


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
