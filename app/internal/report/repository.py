"""Repository interface for report data access."""
from abc import ABC, abstractmethod
from datetime import datetime

from app.internal.report.schemas import GeneralJournalEntry


class ReportRepository(ABC):
    """Abstract repository for reports."""

    @abstractmethod
    def get_general_journal_entries(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[GeneralJournalEntry]:
        """Get general journal entries for a company within a date range."""
        pass
