from datetime import UTC, datetime

from pydantic import EmailStr

from app.domain.entities.vendor import Company


class VendorBuilder:
    """Builder pattern for creating Vendor entities"""

    def __init__(self):
        self._vendor = Company(
            name="",
            nit="",
            email="",
        )
        self._vendor.created_at = datetime.now(UTC)

    def with_name(self, name: str) -> "VendorBuilder":
        """Set vendor name"""
        self._vendor.name = name
        return self

    def with_nit(self, nit: str) -> "VendorBuilder":
        """Set vendor NIT"""
        self._vendor.nit = nit
        return self

    def with_date_birth(self, date_birth: str) -> "VendorBuilder":
        """Set vendor birth date"""
        self._vendor.date_birth = date_birth
        return self

    def with_commercial_activity(self, activity: str) -> "VendorBuilder":
        """Set vendor commercial activity"""
        self._vendor.comercial_activity = activity
        return self

    def with_email(self, email: EmailStr) -> "VendorBuilder":
        """Set vendor email"""
        self._vendor.email = email
        return self

    def with_address(self, address: str) -> "VendorBuilder":
        """Set vendor address"""
        self._vendor.address = address
        return self

    def with_created_by(self, created_by: str) -> "VendorBuilder":
        """Set who created the vendor"""
        self._vendor.created_by = created_by
        return self

    def with_updated_by(self, updated_by: str) -> "VendorBuilder":
        """Set who updated the vendor"""
        self._vendor.updated_by = updated_by
        self._vendor.updated_at = datetime.now(UTC)
        return self

    def build(self) -> Company:
        """Build and return the vendor instance"""
        # Validate required fields
        if not self._vendor.name:
            raise ValueError("Vendor name is required")
        if not self._vendor.nit:
            raise ValueError("Vendor NIT is required")
        if not self._vendor.email:
            raise ValueError("Vendor email is required")
        if not self._vendor.created_by:
            raise ValueError("Created by is required")

        return self._vendor

    @classmethod
    def create_vendor(
        cls,
        name: str,
        nit: str,
        email: EmailStr,
        created_by: str,
        date_birth: str | None = None,
        commercial_activity: str | None = None,
        address: str | None = None,
    ) -> Company:
        """Convenience method to create a vendor with required fields"""
        builder = cls()
        builder.with_name(name).with_nit(nit).with_email(
            email
        ).with_created_by(created_by)

        if date_birth:
            builder.with_date_birth(date_birth)
        if commercial_activity:
            builder.with_commercial_activity(commercial_activity)
        if address:
            builder.with_address(address)

        return builder.build()
