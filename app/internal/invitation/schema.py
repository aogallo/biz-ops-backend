"""Invitation API schemas for requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvitationCreate(BaseModel):
    """Schema for creating a new invitation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr
    organization_id: UUID = Field(
        alias="organizationId", serialization_alias="organizationId"
    )
    default_role: str | None = Field(
        default=None, alias="defaultRole", serialization_alias="defaultRole"
    )
    company_ids: list[UUID] | None = Field(
        default=None, alias="companyIds", serialization_alias="companyIds"
    )


class InvitationResponse(BaseModel):
    """Schema for invitation response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    token: str
    email: EmailStr
    organization_id: UUID = Field(
        alias="organizationId", serialization_alias="organizationId"
    )
    status: str  # "pending", "accepted", "expired", "revoked"
    invited_by: UUID = Field(
        alias="invitedBy", serialization_alias="invitedBy"
    )
    default_role: str | None = Field(
        alias="defaultRole", serialization_alias="defaultRole"
    )
    expires_at: datetime = Field(
        alias="expiresAt", serialization_alias="expiresAt"
    )
    created_at: datetime = Field(
        alias="createdAt", serialization_alias="createdAt"
    )
    accepted_at: datetime | None = Field(
        default=None, alias="acceptedAt", serialization_alias="acceptedAt"
    )


class InvitationListResponse(BaseModel):
    """Schema for list of invitations response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    invitations: list[InvitationResponse]
    total: int


class InvitationAcceptRequest(BaseModel):
    """Schema for accepting an invitation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    password: str | None = None  # For email/password auth
    oauth_provider: str | None = Field(
        default=None,
        alias="oauthProvider",
        serialization_alias="oauthProvider",
    )  # "google" or "github"
    oauth_code: str | None = Field(
        default=None, alias="oauthCode", serialization_alias="oauthCode"
    )


class InvitationAcceptResponse(BaseModel):
    """Schema for invitation acceptance response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_token: str = Field(
        alias="accessToken", serialization_alias="accessToken"
    )
    refresh_token: str | None = Field(
        default=None, alias="refreshToken", serialization_alias="refreshToken"
    )
    user: dict  # UserRead schema


class InvitationVerifyResponse(BaseModel):
    """Schema for invitation token verification response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    valid: bool
    email: EmailStr | None = None
    organization_id: UUID | None = Field(
        default=None,
        alias="organizationId",
        serialization_alias="organizationId",
    )
    expires_at: datetime | None = Field(
        default=None, alias="expiresAt", serialization_alias="expiresAt"
    )
    message: str | None = None
