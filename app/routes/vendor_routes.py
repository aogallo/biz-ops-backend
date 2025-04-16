from typing import Annotated
from fastapi import APIRouter, Body, Depends

from app.dependencies import verify_token
from app.domain.entities.vendor import VendorCreate
from app.infrastructure.database import SessionDep
from app.infrastructure.repositories.vendor_respository_impl import VendorRepositoryImpl
from app.services.vendro_service import VendorService


router = APIRouter(prefix="/vendor", tags=["vendor"])


@router.post("/")
def create_vendor(
    current_user=Depends(verify_token()),
    session=SessionDep,
    new_vendor=Annotated[VendorCreate, Body(embed=True)],
):
    vendor_repo = VendorRepositoryImpl(session, current_user=current_user)
    vendor_service = VendorService(vendor_repo)

    return vendor_service
