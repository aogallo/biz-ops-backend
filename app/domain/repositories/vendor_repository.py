from abc import ABC, abstractmethod

from app.domain.entities.vendor import Vendor, VendorCreate
from app.domain.repositories.base_repository import BaseRepository


class VendorRepository(ABC, BaseRepository):
    @abstractmethod
    def create(self, vendor: VendorCreate) -> Vendor:
        pass
