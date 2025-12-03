from sqlmodel import Session, select

from app.internal.journal.entity import JournalEntry, JournalEntryCreate
from app.internal.journal.repository import JournalEntryRepository
from app.internal.user.entity import User


class JournalEntryRepositoryImpl(JournalEntryRepository):
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
        return new_journal_entry

    def get_by_invoice_id(self, id: int) -> JournalEntry | None:
        statement = select(JournalEntry).where(JournalEntry.invoice_id == id)
        result: JournalEntry | None = self.db.exec(statement).one_or_none()
        return result
