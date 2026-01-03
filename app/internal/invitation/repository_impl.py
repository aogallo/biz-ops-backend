"""SQLModel implementation of invitation repository."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.internal.invitation.entity import Invitation, InvitationStatus
from app.internal.invitation.repository import InvitationRepository
from app.internal.user.entity import User


class InvitationRepositoryImpl(InvitationRepository):
    """SQLModel implementation of invitation repository."""

    def __init__(self, session: Session, current_user: User):
        """Initialize repository with database session and current user.

        Args:
            session: Database session
            current_user: Current authenticated user
        """
        self.db = session
        self.current_user = current_user

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
        invitation = Invitation(
            email=email,
            organization_id=organization_id,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at,
            default_role=default_role,
            status=InvitationStatus.PENDING,
        )
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        return invitation

    def get_by_id(self, invitation_id: UUID) -> Invitation | None:
        """Get invitation by ID."""
        return self.db.get(Invitation, invitation_id)

    def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token."""
        statement = select(Invitation).where(Invitation.token == token)
        return self.db.exec(statement).first()

    def get_by_email(
        self, email: str, organization_id: UUID
    ) -> list[Invitation]:
        """Get all invitations for an email in an organization."""
        statement = select(Invitation).where(
            Invitation.email == email,
            Invitation.organization_id == organization_id,
        )
        return list(self.db.exec(statement).all())

    def get_all_by_organization(
        self,
        organization_id: UUID,
        status: InvitationStatus | None = None,
    ) -> list[Invitation]:
        """Get all invitations for an organization, optionally filtered by status."""
        statement = select(Invitation).where(
            Invitation.organization_id == organization_id
        )

        if status:
            statement = statement.where(Invitation.status == status)

        return list(self.db.exec(statement).all())

    def update_status(
        self,
        invitation_id: UUID,
        status: InvitationStatus,
        accepted_at: datetime | None = None,
    ) -> None:
        """Update invitation status."""
        invitation = self.get_by_id(invitation_id)
        if invitation:
            invitation.status = status
            if accepted_at:
                invitation.accepted_at = accepted_at
            self.db.add(invitation)
            self.db.commit()

    def delete_invitation(self, invitation_id: UUID) -> None:
        """Delete an invitation."""
        invitation = self.get_by_id(invitation_id)
        if invitation:
            self.db.delete(invitation)
            self.db.commit()

    def revoke_pending_invitations(
        self, email: str, organization_id: UUID
    ) -> None:
        """Revoke all pending invitations for an email in an organization."""
        invitations = self.get_by_email(email, organization_id)
        for invitation in invitations:
            if invitation.status == InvitationStatus.PENDING:
                invitation.status = InvitationStatus.REVOKED
                self.db.add(invitation)
        self.db.commit()
