from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, verify_token
from app.infrastructure.database import get_session
from app.schemas.invoice_schema import InvoiceListResponse, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.get("/", response_model=InvoiceListResponse)
def list_invoices(current_user=Depends(get_current_user)):
    """List all invoices."""
    service = InvoiceService(current_user)
    invoices = service.list_all_invoices()
    return InvoiceListResponse(
        invoices=[InvoiceResponse.model_validate(i) for i in invoices],
        total=len(invoices),
    )
