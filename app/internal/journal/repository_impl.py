from uuid import UUID

from sqlmodel import Session, func, select

from app.internal.journal.entity import JournalEntry, JournalEntryCreate
from app.internal.journal.repository import JournalEntryRepository
from app.internal.user.entity import User


class JournalEntryRepositoryImpl(JournalEntryRepository):
    """
    Implementation of Journal Entry Repository.
    All queries are automatically scoped to company_id for multi-tenancy.
    """

    def __init__(
        self, session: Session, current_user: User, company_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.company_id = company_id  # Company context for multi-tenancy

    def create(self, journal_entry: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry scoped to this company"""
        journal_entry_data = journal_entry.model_dump()
        journal_entry_data["company_id"] = self.company_id
        journal_entry_data["created_by"] = self.current_user.auth0_user_id

        new_journal_entry = JournalEntry(**journal_entry_data)
        self.db.add(new_journal_entry)
        self.db.commit()
        self.db.refresh(new_journal_entry)
        return new_journal_entry

    def get_by_invoice_id(self, invoice_id: UUID) -> list[JournalEntry]:
        """Get journal entries by invoice id (scoped to company)"""
        statement = select(JournalEntry).where(
            JournalEntry.company_id == self.company_id,
            JournalEntry.invoice_id == invoice_id,
        )
        result: list[JournalEntry] = self.db.exec(statement)._allrows()
        return result

    def add_bulk(
        self, journal_entries: list[JournalEntry]
    ) -> list[JournalEntry]:
        """Add bulk journal entries (automatically scoped to company)"""
        # Set company_id and created_by for all journal entries
        for entry in journal_entries:
            entry.company_id = self.company_id
            entry.created_by = self.current_user.auth0_user_id

        self.db.add_all(journal_entries)
        self.db.commit()
        for journal_entry in journal_entries:
            self.db.refresh(journal_entry)
        return journal_entries

    def get_by_debit_invoice_id(
        self, invoice_id: UUID, debit: float
    ) -> JournalEntry:
        """Get a journal entry by debit and invoice id (scoped to company)"""
        statement = select(JournalEntry).where(
            JournalEntry.company_id == self.company_id,
            JournalEntry.invoice_id == invoice_id,
            JournalEntry.debit == debit,
        )
        result: JournalEntry = self.db.exec(statement).one()
        return result

    def get_by_credit_invoice_id(
        self, invoice_id: UUID, credit: float
    ) -> JournalEntry:
        """Get a journal entry by credit and invoice id (scoped to company)"""
        statement = select(JournalEntry).where(
            JournalEntry.company_id == self.company_id,
            JournalEntry.invoice_id == invoice_id,
            JournalEntry.credit == credit,
        )
        result: JournalEntry = self.db.exec(statement).one()
        return result

    def update_by_id(self, journal_entry: JournalEntry) -> JournalEntry:
        """Update a journal entry (must belong to this company)"""
        # Verify journal entry belongs to this company
        if journal_entry.company_id != self.company_id:
            raise ValueError(
                f"Journal entry does not belong to company {self.company_id}"
            )

        journal_entry.updated_by = self.current_user.auth0_user_id
        self.db.add(journal_entry)
        self.db.commit()
        self.db.refresh(journal_entry)
        return journal_entry

    def get_by_id(self, id: UUID) -> list[JournalEntry] | None:
        """Get a journal entry by id (scoped to company)"""
        statement = select(JournalEntry).where(
            JournalEntry.company_id == self.company_id,
            JournalEntry.id == id,
        )
        result: list[JournalEntry] | None = self.db.exec(statement)._allrows()
        return result

    def get_all(self, offset: int = 0, limit: int = 100) -> list[JournalEntry]:
        """Get all journal entries (scoped to company)"""
        statement = (
            select(JournalEntry)
            .where(JournalEntry.company_id == self.company_id)
            .offset(offset)
            .limit(limit)
        )
        result: list[JournalEntry] = self.db.exec(statement)._allrows()
        return result

    def get_count(self) -> int:
        """Get count of journal entries (scoped to company)"""
        statement = (
            select(func.count())
            .select_from(JournalEntry)
            .where(JournalEntry.company_id == self.company_id)
        )
        count: int = self.db.exec(statement).one()
        return count
