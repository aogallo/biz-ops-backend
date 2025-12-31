"""API routes for reports."""

import os
import tempfile
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import (
    get_current_user,
    verify_company_access,
    verify_token,
)
from app.internal.report.schemas import GeneralJournalReport, SalesLedgerReport
from app.internal.report.service import ReportService

router = APIRouter(
    prefix="/companies/{company_id}/reports",
    tags=["reports"],
    dependencies=[Depends(verify_token)],
)


@router.get("/general-journal", response_model=GeneralJournalReport)
def get_general_journal_report(
    company_id: UUID,
    start_date: datetime | None = Query(
        None, description="Start date for the report (ISO format)"
    ),
    end_date: datetime | None = Query(
        None, description="End date for the report (ISO format)"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    _: None = Depends(verify_company_access),
):
    """
    Get the general journal report for a company.

    Returns all journal entries with:
    - Date
    - Account number
    - Account name
    - Transaction concept (description)
    - Debit amount
    - Credit amount
    - Folio number (invoice ID)

    The report includes totals for debits and credits.
    """
    service = ReportService(session, current_user, company_id)
    return service.get_general_journal_report(
        start_date=start_date, end_date=end_date
    )


@router.get("/general-journal/pdf")
def download_general_journal_pdf(
    company_id: UUID,
    start_date: datetime | None = Query(
        None, description="Start date for the report (ISO format)"
    ),
    end_date: datetime | None = Query(
        None, description="End date for the report (ISO format)"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _: None = Depends(verify_company_access),
):
    """
    Download the general journal report as a PDF file.

    Returns a PDF file with formatted general journal entries including:
    - Company name and NIT header
    - Date range
    - Formatted table with all journal entries
    - Total debits and credits
    - Generation timestamp

    The PDF will be downloaded with a descriptive filename.
    """
    service = ReportService(session, current_user, company_id)

    # Generate PDF bytes
    pdf_bytes = service.generate_general_journal_pdf(
        start_date=start_date, end_date=end_date
    )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    # Generate filename
    filename = _generate_pdf_filename(
        company_id,
        "general_journal",
        start_date,
        end_date,
    )

    # Schedule cleanup
    background_tasks.add_task(os.unlink, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _generate_pdf_filename(
    company_id: UUID,
    filename: str,
    start_date: datetime | None,
    end_date: datetime | None,
) -> str:
    """Generate descriptive filename for PDF download."""
    base = f"{filename}_company{str(company_id)[:8]}"

    if start_date and end_date:
        date_range = (
            f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        )
    elif start_date:
        date_range = f"from_{start_date.strftime('%Y%m%d')}"
    elif end_date:
        date_range = f"until_{end_date.strftime('%Y%m%d')}"
    else:
        date_range = "all_dates"

    return f"{base}_{date_range}.pdf"


@router.get("/sales-ledger", response_model=SalesLedgerReport)
def get_sales_ledger_report(
    company_id: UUID,
    start_date: datetime | None = Query(
        None, description="Start date for the report (ISO format)"
    ),
    end_date: datetime | None = Query(
        None, description="End date for the report (ISO format)"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    _: None = Depends(verify_company_access),
):
    """
    Get the sales ledger report for a company.

    Returns all journal entries with:
    - Date
    - DTE Type
    - Transaction Type
    - Serie
    - Number document
    - NIT
    - Name (BusinessPartner)
    - Amount
    - IVA
    - Total

    """

    service = ReportService(session, current_user, company_id)
    return service.get_sales_ledger_report(
        start_date=start_date, end_date=end_date
    )


@router.get("/sales-ledger/pdf")
def download_sales_ledger_pdf(
    company_id: UUID,
    start_date: datetime | None = Query(
        None, description="Start date for the report (ISO format)"
    ),
    end_date: datetime | None = Query(
        None, description="End date for the report (ISO format)"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _: None = Depends(verify_company_access),
):
    """
    Download the sales ledger report as a PDF file.

    Returns a PDF file with formatted general journal entries including:
    - Company name and NIT header
    - Date range
    - Formatted table with all journal entries

    The PDF will be downloaded with a descriptive filename.
    """
    service = ReportService(session, current_user, company_id)

    # Generate PDF bytes
    pdf_bytes = service.generate_sales_ledger_pdf(
        start_date=start_date,
        end_date=end_date,
    )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    # Generate filename
    filename = _generate_pdf_filename(
        company_id,
        "sales_ledger",
        start_date,
        end_date,
    )

    # Schedule cleanup
    background_tasks.add_task(os.unlink, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
