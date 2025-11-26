from datetime import datetime

from app.schemas.base import CamelCaseSchema


class AccountCreate(CamelCaseSchema):
    """Schema for creating a new account."""

    name: str
    account_number: str
    type: str


class AccountResponse(CamelCaseSchema):
    """Schema for account response."""

    id: int
    name: str
    account_number: str
    type: str
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None
