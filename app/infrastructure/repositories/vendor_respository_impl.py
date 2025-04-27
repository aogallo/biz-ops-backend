from fastapi import Depends
from sqlmodel import Session
from app.domain.entities.vendor import Vendor, VendorCreate
from app.domain.repositories.vendor_repository import VendorRepository
from app.infrastructure.database import get_session


class VendorRepositoryImpl(VendorRepository):
    def __init__(self, db: Session = Depends(get_session)) -> None:
        self.db = db

    def create(self, vendor: VendorCreate) -> Vendor:
        new_vendor = Vendor(
            name=vendor.name,
            nit=vendor.nit,
            date_birth=vendor.date_birth,
            comercial_activity=vendor.comercial_activity,
            address=vendor.address,
            email=vendor.email,
        )
        self.db.add(new_vendor)
        self.db.commit()

        print(new_vendor)

        return new_vendor
