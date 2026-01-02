from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.organization.entity import Organization
from app.internal.organization.repository_impl import (
    OrganizationRepositoryImpl,
)
from app.internal.organization.schema import (
    OrganizationList,
)
from app.internal.user.entity import User


class OrganizationService:
    def __init__(
        self,
        session: Session,
        current_user: User,
    ) -> None:
        self.repository = OrganizationRepositoryImpl(
            session=session,
            current_user=current_user,
        )

    def create_organization(self, organization: Organization):
        db_org = self.repository.get_by_name(name=organization.name)

        if db_org is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The organization already exists",
            )

        return self.repository.create(organization)

    def get_organizations(self, offset: int, limit: int):
        count = self.repository.get_count()
        organizations = self.repository.get_all(offset, limit)

        return OrganizationList(count=count, organizations=organizations)

    def update_organization_by_id(self, id: int, organization):
        db_org = self.repository.get_by_id(id)

        if not db_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        org_data = Organization(**organization.model_dump(exclude_unset=True))
        db_org.sqlmodel_update(org_data)

        return self.repository.update(db_org)
