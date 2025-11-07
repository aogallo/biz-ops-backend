from abc import ABC, abstractmethod

from app.domain.entities.vendor import Vendor, VendorCreate


class VendorRepository(ABC):
    @abstractmethod
    def create_vendor(self, vendor: VendorCreate) -> Vendor:
        pass

    @abstractmethod
    def get_vendor_by_id(self, auth_id: str) -> Vendor | None:
        pass

    @abstractmethod
    def get_all_vendors(self) -> list[Vendor]:
        pass

    @abstractmethod
    def get_vendor_by_email(self, email: str) -> Vendor | None:
        pass
