"""Business logic for invitation management."""

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.invitation.entity import Invitation, InvitationStatus
from app.internal.invitation.repository_impl import InvitationRepositoryImpl
from app.internal.user.entity import User


class InvitationService:
    """Service for invitation business logic."""

    def __init__(self, session: Session, current_user: User):
        """Initialize service with database session and current user.

        Args:
            session: Database session
            current_user: Current authenticated user
        """
        self.repository = InvitationRepositoryImpl(session, current_user)
        self.current_user = current_user

    def create_invitation(
        self,
        email: str,
        organization_id: UUID,
        default_role: str | None = None,
        company_ids: list[UUID] | None = None,
    ) -> Invitation:
        """Create a new invitation.

        Args:
            email: Invitee email address
            organization_id: Organization ID
            default_role: Default role to assign
            company_ids: Optional list of company IDs for access

        Returns:
            Created invitation

        Raises:
            HTTPException: 400 if validation fails
        """
        # Generate secure token (256-bit)
        token = secrets.token_urlsafe(32)

        # Set expiration (7 days from now)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # Revoke any pending invitations for this email in this organization
        self.repository.revoke_pending_invitations(email, organization_id)

        # Create new invitation
        return self.repository.create_invitation(
            email=email,
            organization_id=organization_id,
            token=token,
            invited_by=self.current_user.id,
            expires_at=expires_at,
            default_role=default_role,
        )

    def list_invitations(
        self,
        organization_id: UUID,
        status: InvitationStatus | None = None,
    ) -> list[Invitation]:
        """List invitations for an organization.

        Args:
            organization_id: Organization ID
            status: Optional status filter

        Returns:
            List of invitations
        """
        return self.repository.get_all_by_organization(
            organization_id=organization_id, status=status
        )

    def get_invitation_by_id(self, invitation_id: UUID) -> Invitation:
        """Get invitation by ID.

        Args:
            invitation_id: Invitation ID

        Returns:
            Invitation

        Raises:
            HTTPException: 404 if not found
        """
        invitation = self.repository.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invitation with ID '{invitation_id}' not found",
            )
        return invitation

    def verify_token(self, token: str) -> dict:
        """Verify invitation token.

        Args:
            token: Invitation token

        Returns:
            Dict with verification result
        """
        invitation = self.repository.get_by_token(token)

        if not invitation:
            return {
                "valid": False,
                "message": "Invalid invitation token",
            }

        # Check if already used
        if invitation.status != InvitationStatus.PENDING:
            return {
                "valid": False,
                "message": f"Invitation already {invitation.status.value}",
            }

        # Check if expired
        if datetime.now(timezone.utc) > invitation.expires_at:
            # Mark as expired
            self.repository.update_status(
                invitation.id, InvitationStatus.EXPIRED
            )
            return {
                "valid": False,
                "message": "Invitation has expired",
            }

        return {
            "valid": True,
            "email": invitation.email,
            "organization_id": str(invitation.organization_id),
            "expires_at": invitation.expires_at.isoformat(),
        }

    def accept_invitation(
        self,
        token: str,
        password: str | None = None,
        oauth_provider: str | None = None,
        oauth_code: str | None = None,
    ) -> dict:
        """Accept an invitation and create user account.

        Args:
            token: Invitation token
            password: Password for email/password auth
            oauth_provider: OAuth provider ("google" or "github")
            oauth_code: OAuth authorization code

        Returns:
            Dict with access token and user data

        Raises:
            HTTPException: 400/404 if validation fails
        """
        # Verify token first
        verification = self.verify_token(token)
        if not verification["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verification["message"],
            )

        invitation = self.repository.get_by_token(token)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        # TODO: Phase 3 implementation
        # 1. Create User account (email/password or OAuth)
        # 2. Link to organization
        # 3. Create UserCompanyAccess entries
        # 4. Mark invitation as accepted
        # 5. Generate access token
        # 6. Return token + user data

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Invitation acceptance not yet implemented (Phase 3)",
        )

    def delete_invitation(self, invitation_id: UUID) -> None:
        """Delete an invitation.

        Args:
            invitation_id: Invitation ID

        Raises:
            HTTPException: 404 if not found
        """
        invitation = self.repository.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invitation with ID '{invitation_id}' not found",
            )

        self.repository.delete_invitation(invitation_id)
