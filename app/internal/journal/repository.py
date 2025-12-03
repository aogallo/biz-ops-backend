from abc import ABC, abstractmethod

from app.internal.journal.entity import JournalEntryCreate


class JournalEntryRepository(ABC):
    @abstractmethod
    def create(self, journal_entry: JournalEntryCreate):
        pass
