"""Vendor API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class VendorBase(BaseModel):
    """Base vendor schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""

    pass


class VendorUpdate(BaseModel):
    """Schema for updating a vendor."""

    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class VendorResponse(VendorBase):
    """Schema for vendor response."""

    id: int
    created_by: str
    created_at: datetime
    updated_by: str | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class VendorListResponse(BaseModel):
    """Schema for list of vendors response."""

    vendors: list[VendorResponse]
    total: int = Field(description="Total number of vendors")
