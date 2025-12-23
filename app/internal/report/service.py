"""Service for generating reports."""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session

from app.internal.company.repostiory_impl import CompanyRepositoryImpl
from app.internal.report.general_journal_pdf_generator import (
    GeneralJournalPDFGenerator,
)
from app.internal.report.repository_impl import ReportRepositoryImpl
from app.internal.report.sales_ledger_pdf_generator import (
    SalesLedgerPDFGenerator,
)
from app.internal.report.schemas import GeneralJournalReport, SalesLedgerReport
from app.internal.user.entity import User


class ReportService:
    """Service for managing reports."""

    def __init__(self, session: Session, current_user: User) -> None:
        self._report_repo = ReportRepositoryImpl(session)
        self._company_repo = CompanyRepositoryImpl(session, current_user)

    def get_general_journal_report(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> GeneralJournalReport:
        """
        Generate a general journal report for a company.

        Args:
            company_id: The company ID to generate the report for
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            GeneralJournalReport with entries and totals
        """
        entries = self._report_repo.get_general_journal_entries(
            company_id=company_id, start_date=start_date, end_date=end_date
        )

        # Calculate totals
        total_debits = sum(entry.debit for entry in entries)
        total_credits = sum(entry.credit for entry in entries)

        return GeneralJournalReport(
            entries=entries,
            total_debits=total_debits,
            total_credits=total_credits,
            count=len(entries),
        )

    def generate_general_journal_pdf(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> bytes:
        """
        Generate PDF for general journal report.

        Args:
            company_id: The company ID to generate the report for
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            PDF as bytes

        Raises:
            HTTPException: If company not found or date range is invalid
        """
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before or equal to end date",
            )

        # Get company info
        company = self._company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with ID {company_id} not found",
            )

        # Get report data (reuse existing method)
        report_data = self.get_general_journal_report(
            company_id=company_id, start_date=start_date, end_date=end_date
        )

        # Generate PDF
        generator = GeneralJournalPDFGenerator()
        pdf_bytes = generator.generate(
            report_data=report_data,
            company_name=company.name,
            company_nit=company.nit,
            start_date=start_date,
            end_date=end_date,
        )

        return pdf_bytes

    def get_sales_ledger_report(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SalesLedgerReport:
        """
        Generate a sales ledger report for a company.

        Args:
            company_id: The company ID to generate the report for
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            SalesLedgerReport with entries and count
        """
        entries = self._report_repo.get_sales_ledger_entries(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        return SalesLedgerReport(entries=entries, count=len(entries))

    def generate_sales_ledger_pdf(
        self,
        company_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> bytes:
        """
        Generate PDF for general journal report.

        Args:
            company_id: The company ID to generate the report for
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            PDF as bytes

        Raises:
            HTTPException: If company not found or date range is invalid
        """
        print("dates.......", start_date, end_date)
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before or equal to end date",
            )

        # Get company info
        company = self._company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with ID {company_id} not found",
            )

        # Get report data (reuse existing method)
        report_data = self.get_sales_ledger_report(
            company_id=company_id, start_date=start_date, end_date=end_date
        )

        # Generate PDF
        generator = SalesLedgerPDFGenerator()
        pdf_bytes = generator.generate(
            report_data=report_data,
            company_name=company.name,
            company_nit=company.nit,
            start_date=start_date,
            end_date=end_date,
        )

        return pdf_bytes
