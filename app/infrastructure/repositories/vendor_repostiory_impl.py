from sqlmodel import select

from app.domain.entities.vendor import Vendor, VendorCreate
from app.domain.repositories.vendor_repository import VendorRepository


class VendorRepositoryImpl(VendorRepository):
    def create(self, model: Vendor) -> Vendor:
        """Create a new vendor"""
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_by_id(self, id: int) -> Vendor | None:
        """Get vendor by ID"""
        return self.db.get(Vendor, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Vendor]:
        """Get all vendors with pagination"""
        statement = select(Vendor).offset(skip).limit(limit)
        result = self.db.exec(statement)
        return list(result)

    def update(self, id: int, model: Vendor) -> Vendor:
        """Update an existing vendor"""
        db_vendor = self.db.get(Vendor, id)
        if not db_vendor:
            raise ValueError(f"Vendor with id {id} not found")

        vendor_data = model.model_dump(exclude_unset=True)
        for field, value in vendor_data.items():
            setattr(db_vendor, field, value)

        self.db.add(db_vendor)
        self.db.commit()
        self.db.refresh(db_vendor)
        return db_vendor

    def delete(self, id: int) -> bool:
        """Delete a vendor by ID"""
        vendor = self.db.get(Vendor, id)
        if not vendor:
            return False

        self.db.delete(vendor)
        self.db.commit()
        return True

    def exists(self, id: int) -> bool:
        """Check if vendor exists by ID"""
        vendor = self.db.get(Vendor, id)
        return vendor is not None

    # Custom vendor methods
    def create_vendor(self, vendor: VendorCreate) -> Vendor:
        """Create a new vendor using VendorCreate schema"""
        new_vendor = Vendor(**vendor.model_dump())
        return self.create(new_vendor)

    def get_vendor_by_id(self, vendor_id: int) -> Vendor | None:
        """Get vendor by ID (alias for get_by_id)"""
        return self.get_by_id(vendor_id)

    def get_all_vendors(self) -> list[Vendor]:
        """Get all vendors (alias for get_all)"""
        return self.get_all()

    def get_vendor_by_email(self, email: str) -> Vendor | None:
        """Get vendor by email"""
        statement = select(Vendor).where(Vendor.email == email)
        result = self.db.exec(statement)
        return result.first()

    def get_vendor_by_nit(self, nit: str) -> Vendor | None:
        """Get vendor by NIT"""
        statement = select(Vendor).where(Vendor.nit == nit)
        result = self.db.exec(statement)
        return result.first()

    def search_vendors(self, search_term: str) -> list[Vendor]:
        """Search vendors by name or NIT"""
        statement = select(Vendor).where(
            (Vendor.name.ilike(f"%{search_term}%"))
            | (Vendor.nit.ilike(f"%{search_term}%"))
        )
        result = self.db.exec(statement)
        return list(result)
