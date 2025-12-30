from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.internal.shared.camel_case import to_camel


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    name: str
    slug: str
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    settings: dict = {}
    is_active: bool = True


class OrganizationResponse(OrganizationCreate):
    id: UUID
