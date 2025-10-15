from app.domain.repositories.vendor_repository import VendorRepository
from app.schemas.vendor_schema import VendorCreate


class VendorRepository(VendorRepository):
    def create_user(self, vendor: VendorCreate):
        pass
