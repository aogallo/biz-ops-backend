"""User API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    picture: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    auth_id: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    picture: str | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    auth_id: str
    created_by: str
    created_at: datetime
    updated_by: str | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for list of users response."""

    users: list[UserResponse]
    total: int = Field(description="Total number of users")
