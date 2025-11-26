from fastapi import APIRouter, Depends, Response, UploadFile

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
from app.schemas.invoice_detail_schema import InvoiceDetailResponse
from app.schemas.invoice_schema import InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.get("", response_model=list[InvoiceResponse])
def list_invoices(current_user=Depends(get_current_user)):
    """List all invoices."""
    service = InvoiceService(current_user)
    invoices = service.list_all_invoices()
    return invoices


@router.get("/{id}/details", response_model=list[InvoiceDetailResponse])
def get_invoice_details(id: int, current_user=Depends(get_current_user)):
    """List all invoices."""
    service = InvoiceService(current_user)
    invoice_details = service.get_invoice_deatils(id)
    return invoice_details


@router.get("/{id}", response_model=InvoiceResponse)
def get_invoice(id: int, current_user=Depends(get_current_user)):
    """List all invoices."""
    service = InvoiceService(current_user)
    invoice = service.get_invoice_by_id(id)
    return invoice


@router.post("/upload")
async def upload_file(
    file: UploadFile, current_user=Depends(get_current_user)
):
    file_bytes = await file.read()

    service = InvoiceService(current_user)

    service.process_file(file_bytes)

    return Response(status_code=200)
