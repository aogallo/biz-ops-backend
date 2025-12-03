from sqlmodel import Session, select

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

    def get_by_invoice_id(self, invoice_id: int) -> JournalEntry | None:
        """Get a journal entry by invoice id"""
        statement = select(JournalEntry).where(
            JournalEntry.invoice_id == invoice_id
        )
        result: JournalEntry | None = self.db.exec(statement).one_or_none()
        return result

    def add_bulk(self, journal_entries: list[JournalEntry]):
        """Add bulk journal entries"""
        self.db.add_all(journal_entries)
        self.db.commit()
        for journal_entry in journal_entries:
            self.db.refresh(journal_entry)
        return journal_entries
