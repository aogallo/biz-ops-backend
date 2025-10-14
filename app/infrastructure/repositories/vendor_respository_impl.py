from sqlmodel import Session
from app.domain.entities.vendor import Vendor, VendorCreate
from app.domain.repositories.vendor_repository import VendorRepository
from app.infrastructure.database import context


class VendorRepositoryImpl(VendorRepository):
    def create(self, vendor: VendorCreate) -> Vendor:
        new_vendor = Vendor(
            name=vendor.name,
            nit=vendor.nit,
            date_birth=vendor.date_birth,
            comercial_activity=vendor.comercial_activity,
            address=vendor.address,
            email=vendor.email,
            created_by=context.current_user.auth_id
        )
        self.db.add(new_vendor)
        self.db.commit()
        return new_vendor
