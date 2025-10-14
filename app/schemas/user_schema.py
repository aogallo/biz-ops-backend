"""User API schemas for requests and responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    auth_id: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    picture: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""

    auth_id: str
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for list of users response."""

    users: list[UserResponse]
    total: int = Field(description="Total number of users")



