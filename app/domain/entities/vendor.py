from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Vendor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str
    comercial_activity: str
    email: EmailStr
    address: str

    created_by: str = Field(index=True, default="test")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(default=None, index=True)
    udpated_at: Optional[datetime] = Field(default=None)


class VendorCreate:
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str
    comercial_activity: str
    email: EmailStr
    address: str

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
