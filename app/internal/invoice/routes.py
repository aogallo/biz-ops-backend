import logging

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.invoice.entity import InvoiceUpdate as InvoiceUpdateEntity
from app.internal.invoice.entity import (
    InvoiceUpdateAccount as InvoiceUpdateAccountEntity,
)
from app.internal.invoice.schema import (
    InvoiceDetailResponse,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceType,
    InvoiceUpdate,
    InvoiceUpdateAccount,
)
from app.internal.invoice.service import InvoiceService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.get("", response_model=InvoiceListResponse)
def list_invoices(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all invoices with pagination."""
    offset = calculate_offset(page=page, page_size=limit)

    service = InvoiceService(session, current_user)
    result = service.list_all_invoices(offset, limit)

    pagination = PaginationResponse(
        total=result.count,
        page_index=page - 1,
        page_size=limit,
    )

    # Convert entities to response schemas
    invoices_response = [
        InvoiceResponse.model_validate(invoice) for invoice in result.invoices
    ]

    return InvoiceListResponse(
        data=invoices_response,
        pagination=pagination,
    )


@router.get("/{id}/details", response_model=list[InvoiceDetailResponse])
def get_invoice_details(
    id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List invoice details."""
    service = InvoiceService(session, current_user)
    invoice_details = service.get_invoice_deatils(id)
    return invoice_details


@router.get("/{id}", response_model=InvoiceResponse)
def get_invoice(
    id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List an invoice by id."""
    service = InvoiceService(session, current_user)
    invoice = service.get_invoice_by_id(id)
    return invoice


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    invoiceType: InvoiceType = Form(...),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    file_bytes = await file.read()

    service = InvoiceService(session, current_user)

    service.process_file(file_bytes, invoiceType)

    return Response(status_code=200)


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_invoice(
    id: int,
    invoice: InvoiceUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Update an invoice.

    Returns the updated invoice.
    """
    try:
        service = InvoiceService(session, current_user)
        invoice_entity = InvoiceUpdateEntity(
            **invoice.model_dump(exclude_unset=True)
        )
        service.update_invoice_by_id(id, invoice_entity)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_invoice_account(
    id: int,
    invoice: InvoiceUpdateAccount,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Update invoice account.
    """
    try:
        service = InvoiceService(session, current_user)
        invoice_entity = InvoiceUpdateAccountEntity(
            **invoice.model_dump(exclude_unset=True)
        )
        service.update_account_invoice(id, invoice_entity)
    except ValueError as e:
        logger.error("Error to update invoice account message: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
