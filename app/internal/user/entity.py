from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.internal.shared.entity import TimestampMixin

if TYPE_CHECKING:
    from app.internal.company.entity import Company
    from app.internal.journal.entity import JournalEntry
    from app.internal.organization.entity import Organization


class UserAuthenticated(SQLModel):
    """
    Base user
    """

    auth_id: str
    permissions: list[str]


class UserCompanyAccess(SQLModel, table=True):
    """
    Controls which users have access to which companies and their permissions.
    """

    __tablename__ = "user_company_access"

    # Composite primary key
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id", primary_key=True)

    # Role for this user in this company
    role: str = Field(
        default="user"
    )  # "owner", "admin", "accountant", "viewer"

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # Auth0 sub claim of user who granted access

    # Relationships
    user: "User" = Relationship(back_populates="company_accesses")
    company: "Company" = Relationship(back_populates="user_accesses")


class User(TimestampMixin, table=True):
    """
    Users are accountants/staff who work for organizations.
    They can access multiple companies based on user company access.
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Auth0 integration - links to Auth0 user
    auth_id: str  # Auth0 sub claim (inherited concept from UserAuthenticated)
    auth0_user_id: str = Field(unique=True, index=True)

    organization_id: UUID | None = Field(
        default=None,
        foreign_key="organizations.id",
        nullable=True,
        index=True,
    )

    # Contact info
    email: str

    # Status
    is_active: bool = Field(default=False)
    is_email_verified: bool = Field(default=False)
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
