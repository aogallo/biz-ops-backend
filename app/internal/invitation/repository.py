"""Abstract repository interface for invitation operations."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.internal.invitation.entity import Invitation, InvitationStatus


class InvitationRepository(ABC):
    """Abstract base class for invitation repository."""

    @abstractmethod
    def create_invitation(
        self,
        email: str,
        organization_id: UUID,
        token: str,
        invited_by: UUID,
        expires_at: datetime,
        default_role: str | None = None,
    ) -> Invitation:
        """Create a new invitation."""
        pass

    @abstractmethod
    def get_by_id(self, invitation_id: UUID) -> Invitation | None:
        """Get invitation by ID."""
        pass

    @abstractmethod
    def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token."""
        pass

    @abstractmethod
    def get_by_email(
        self, email: str, organization_id: UUID
    ) -> list[Invitation]:
        """Get all invitations for an email in an organization."""
        pass

    @abstractmethod
    def get_all_by_organization(
        self,
        organization_id: UUID,
        status: InvitationStatus | None = None,
    ) -> list[Invitation]:
        """Get all invitations for an organization, optionally filtered by status."""
        pass

    @abstractmethod
    def update_status(
        self,
        invitation_id: UUID,
        status: InvitationStatus,
        accepted_at: datetime | None = None,
    ) -> None:
        """Update invitation status."""
        pass

    @abstractmethod
    def delete_invitation(self, invitation_id: UUID) -> None:
        """Delete an invitation."""
        pass

    @abstractmethod
    def revoke_pending_invitations(
        self, email: str, organization_id: UUID
    ) -> None:
        """Revoke all pending invitations for an email in an organization."""
        pass
