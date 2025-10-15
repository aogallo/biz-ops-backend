from app.infrastructure.repositories.vendor_respository_impl import (
    VendorRepositoryImpl,
)

from app.domain.entities.vendor import VendorCreate


class VendorService:
    def __init__(self) -> None:
        self.repo = VendorRepositoryImpl()

    def create_vendor(self, vendor_data: VendorCreate):
        return self.repo.create(vendor=vendor_data)
