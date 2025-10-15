from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.domain.entities.vendor import VendorCreate
from app.infrastructure.database import get_session
from app.services.vendor_service import VendorService

router = APIRouter(
    prefix="/vendor",
    tags=["vendor"],
    dependencies=[
        Depends(get_session),
        Depends(verify_token),
    ],
)


@router.post("/")
def create_vendor(new_vendor: VendorCreate):
    vendor_service = VendorService()

    return vendor_service.create_vendor(new_vendor)
