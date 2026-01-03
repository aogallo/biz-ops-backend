"""User API schemas for fastapi-users integration."""

from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(schemas.BaseUser[UUID]):
    """
    Schema for reading user data (responses).

    Extends fastapi-users BaseUser with our custom fields.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Custom fields (beyond fastapi-users base fields)
    organization_id: UUID | None = Field(
        default=None, serialization_alias="organizationId"
    )
    first_name: str | None = Field(
        default=None, serialization_alias="firstName"
    )
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    phone: str | None = None
    avatar_url: str | None = Field(
        default=None, serialization_alias="avatarUrl"
    )

    # Auth0 fields (TEMPORARY - Phase 7 removal)
    auth_id: str = Field(serialization_alias="authId")
    auth0_user_id: str = Field(serialization_alias="auth0UserId")


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user (via invitation acceptance).

    Extends fastapi-users BaseUserCreate.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Optional fields for user creation
    first_name: str | None = Field(
        default=None, serialization_alias="firstName"
    )
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    phone: str | None = None
    organization_id: UUID | None = Field(
        default=None, serialization_alias="organizationId"
    )

    # Auth0 fields (TEMPORARY)
    auth_id: str | None = Field(default=None, serialization_alias="authId")
    auth0_user_id: str | None = Field(
        default=None, serialization_alias="auth0UserId"
    )


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating user data.

    Extends fastapi-users BaseUserUpdate with our custom fields.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Custom fields that can be updated
    first_name: str | None = Field(
        default=None, serialization_alias="firstName"
    )
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    phone: str | None = None
    avatar_url: str | None = Field(
        default=None, serialization_alias="avatarUrl"
    )


class UserResponse(BaseModel):
    """
    Custom user response schema with camelCase serialization.

    Used for custom endpoints beyond fastapi-users standard routes.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    email: EmailStr
    is_active: bool = Field(serialization_alias="isActive")
    is_superuser: bool = Field(serialization_alias="isSuperuser")
    is_verified: bool = Field(serialization_alias="isVerified")
    organization_id: UUID | None = Field(
        default=None, serialization_alias="organizationId"
    )
    first_name: str | None = Field(
        default=None, serialization_alias="firstName"
    )
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    phone: str | None = None
    avatar_url: str | None = Field(
        default=None, serialization_alias="avatarUrl"
    )


class UserListResponse(BaseModel):
    """Schema for list of users response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    users: list[UserResponse]
    total: int = Field(description="Total number of users")
