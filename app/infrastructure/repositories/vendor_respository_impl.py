from sqlmodel import Session
from app.domain.entities.vendor import Vendor, VendorCreate
from app.domain.repositories.vendor_repository import VendorRepository


class VendorRepositoryImpl(VendorRepository):
    def __init__(self, db: Session, current_user) -> None:
        self.db = db
        self.current_user = current_user

    def create(self, vendor: VendorCreate) -> Vendor:
        print("current_user", self.current_user)
        new_vendor = Vendor(
            name=vendor.name,
            nit=vendor.nit,
            date_birth=vendor.date_birth,
            comercial_activity=vendor.comercial_activity,
            address=vendor.address,
            email=vendor.email,
        )
        self.db.add(new_vendor)
        return new_vendor
