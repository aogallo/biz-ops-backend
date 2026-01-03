"""Invitation entity for user onboarding system."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.organization.entity import Organization
    from app.internal.user.entity import User


class InvitationStatus(str, Enum):
    """Status of user invitation."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invitation(TimestampMixin, table=True):
    """
    User invitations for organization onboarding.

    Invitations are sent by super admins to invite new users to the platform.
    Each invitation contains a secure token that expires after 7 days.
    """

    __tablename__: ClassVar[str] = "invitation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: str = Field(
        unique=True, index=True, max_length=255
    )  # Cryptographically secure token
    email: str = Field(max_length=255, index=True)

    # Multi-tenancy
    organization_id: UUID = Field(
        foreign_key="organization.id", nullable=False, index=True
    )

    # Invitation metadata
    status: InvitationStatus = Field(
        default=InvitationStatus.PENDING, index=True, max_length=20
    )
    invited_by: UUID = Field(
        foreign_key="user.id", nullable=False
    )  # User who sent invitation
    accepted_by: UUID | None = Field(
        foreign_key="user.id", nullable=True, default=None
    )

    # Lifecycle timestamps
    expires_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None

    # Optional: Pre-assign role for UserCompanyAccess
    default_role: str | None = Field(
        default="viewer", max_length=50
    )  # Role to assign on acceptance

    # Optional: Pre-assign company access (list of company UUIDs as JSON)
    company_ids: list[str] | None = Field(
        default=None, sa_column=Column(JSON)
    )  # Company IDs to grant access on acceptance

    # Relationships
    organization: "Organization" = Relationship()
    inviter: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invitation.invited_by]"}
    )
    acceptor: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invitation.accepted_by]"}
    )
