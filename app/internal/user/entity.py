from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.company.entity import Company
    from app.internal.journal.entity import JournalEntry
    from app.internal.organization.entity import Organization
    from app.internal.permission.entity import Role


class UserAuthenticated(SQLModel):
    """
    Base user
    """

    auth_id: str
    permissions: list[str]


class OAuthAccount(SQLModel, table=True):
    """
    Links users to OAuth providers (Google, GitHub, etc.).

    Stores OAuth tokens and account information for federated login.
    """

    __tablename__: ClassVar[str] = "oauth_account"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    oauth_name: str = Field(max_length=100)  # "google", "github"
    access_token: str  # OAuth access token (should be encrypted in production)
    expires_at: int | None = None  # Token expiration timestamp
    refresh_token: str | None = (
        None  # OAuth refresh token (should be encrypted)
    )
    account_id: str = Field(max_length=255)  # Provider's user ID
    account_email: str = Field(max_length=255)  # Email from provider

    # Relationships
    user: "User" = Relationship(back_populates="oauth_accounts")


class UserCompanyAccess(SQLModel, table=True):
    """
    Controls which users have access to which companies and their permissions.
    """

    __tablename__: ClassVar[str] = "user_company_access"

    # Composite primary key
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    company_id: UUID = Field(foreign_key="company.id", primary_key=True)

    # Role for this user in this company
    role: str = Field(
        default="user"
    )  # "owner", "admin", "accountant", "viewer"
    role_id: UUID | None = Field(
        foreign_key="role.id", nullable=True, default=None
    )  # New: FK to role table

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # Auth0 sub claim of user who granted access

    # Relationships
    user: "User" = Relationship(back_populates="company_accesses")
    company: "Company" = Relationship(back_populates="user_accesses")
    role_ref: "Role" = Relationship()


class User(TimestampMixin, table=True):
    """
    Users are accountants/staff who work for organizations.
    They can access multiple companies based on user company access.
    """

    __tablename__: ClassVar[str] = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Auth0 integration - links to Auth0 user (TEMPORARY - will be removed in Phase 7)
    auth_id: str  # Auth0 sub claim (inherited concept from UserAuthenticated)
    auth0_user_id: str = Field(unique=True, index=True)

    # Self-hosted authentication fields (NEW)
    hashed_password: str | None = Field(
        default=None, max_length=255
    )  # Nullable for OAuth-only accounts
    is_superuser: bool = Field(
        default=False
    )  # Super admin flag - only superusers can invite users
    is_verified: bool = Field(
        default=False
    )  # Email verification status (replaces is_email_verified)

    organization_id: UUID | None = Field(
        default=None,
        foreign_key="organization.id",
        nullable=True,
        index=True,
    )

    # Contact info
    email: str

    # Status
    is_active: bool = Field(default=False)
    is_email_verified: bool = Field(
        default=False
    )  # DEPRECATED - use is_verified instead
    last_login_at: datetime | None = None

    # Profile
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)

    # Relationships
    organization: "Organization" = Relationship(back_populates="users")
    company_accesses: list["UserCompanyAccess"] = Relationship(
        back_populates="user"
    )
    journal_entries: list["JournalEntry"] = Relationship(back_populates="user")
    oauth_accounts: list["OAuthAccount"] = Relationship(back_populates="user")
