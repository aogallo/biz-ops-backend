from sqlmodel import Session, func, select

from app.internal.journal.entity import JournalEntry, JournalEntryCreate
from app.internal.journal.repository import JournalEntryRepository
from app.internal.user.entity import User


class JournalEntryRepositoryImpl(JournalEntryRepository):
    """Implementation of Journal Entry Repository"""

    def __init__(self, session: Session, current_user: User) -> None:
        self.db = session
        self.current_user = current_user

    def create(self, journal_entry: JournalEntryCreate):
        journal_entry_data = journal_entry.model_dump()
        journal_entry_data["created_by"] = self.current_user.auth_id

        new_journal_entry = JournalEntry(**journal_entry_data)
        self.db.add(new_journal_entry)
        self.db.commit()
        self.db.refresh(new_journal_entry)

    def get_by_id(self, id: int) -> list[JournalEntry]:
        """Get a journal entry by invoice id"""
        statement = select(JournalEntry).where(JournalEntry.invoice_id == id)
        result: list[JournalEntry] = self.db.exec(statement)._allrows()
        return result

    def add_bulk(self, journal_entries: list[JournalEntry]):
        """Add bulk journal entries"""
        self.db.add_all(journal_entries)
        self.db.commit()
        for journal_entry in journal_entries:
            self.db.refresh(journal_entry)
        return journal_entries

    def get_by_debit_invoice_id(self, id: int, debit: float):
        """Get a journal entry by debit and invoice id"""
        statement = select(JournalEntry).where(
            JournalEntry.invoice_id == id, JournalEntry.debit == debit
        )
        result: JournalEntry = self.db.exec(statement).one()
        return result

    def get_by_credit_invoice_id(self, id: int, credit: float):
        """Get a journal entry by credit and invoice id"""
        statement = select(JournalEntry).where(
            JournalEntry.invoice_id == id, JournalEntry.debit == credit
        )
        result: JournalEntry = self.db.exec(statement).one()
        return result

    def update_by_id(self, journal_entry: JournalEntry):
        """Update a journal entry"""
        self.db.add(journal_entry)
        self.db.commit()
        self.db.refresh(journal_entry)

    def count_journal_entries_by_id(self, id: int):
        """Get count of a journal entry"""
        statement = (
            select(func.count())
            .select_from(JournalEntry)
            .where(JournalEntry.id == id)
        )
        return self.db.exec(statement)
