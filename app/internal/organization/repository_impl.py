from sqlmodel import Session, select

from app.internal.organization.entity import Organization
from app.internal.organization.repository import OrganizationRepository
from app.internal.user.entity import User


class OrganizationRepositoryImpl(OrganizationRepository):
    def __init__(self, session: Session, current_user: User) -> None:
        self.db = session
        self.current_user = current_user

    def create(self, organization: Organization) -> Organization:
        """Create a organization"""
        organization.created_by = self.current_user.auth_id
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def get_by_id(self, organization_id: int) -> Organization | None:
        """Get a organization by id"""
        result: Organization | None = self.db.get(
            Organization, organization_id
        )
        return result

    def delete(self, organization: Organization) -> bool:
        """Delete a organization by id"""
        self.db.delete(organization)
        self.db.commit()
        return True

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Organization]:
        """Get all organizations (scoped to company)"""
        statement = select(Organization).offset(offset).limit(limit)
        result: list[Organization] = self.db.exec(statement)._allrows()
        return result

    def get_by_name(self, name: str) -> Organization | None:
        statement = select(Organization).where(Organization.name == name)
        result: Organization | None = self.db.exec(statement).one_or_none()
        return result
