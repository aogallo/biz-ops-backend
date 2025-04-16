from abc import ABC, abstractmethod

from app.domain.entities.vendor import Vendor, VendorCreate


class VendorRepository(ABC):
    @abstractmethod
    def create(self, vendor: VendorCreate) -> Vendor:
        pass
