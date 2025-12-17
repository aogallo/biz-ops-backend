"""User API schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr
    picture: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    auth_id: str = Field(serialization_alias="authId")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr | None = None
    picture: str | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    auth_id: str = Field(serialization_alias="authId")
    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class UserListResponse(BaseModel):
    """Schema for list of users response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    users: list[UserResponse]
    total: int = Field(description="Total number of users")
