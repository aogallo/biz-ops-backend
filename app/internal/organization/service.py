from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.organization.entity import Organization
from app.internal.organization.repository_impl import (
    OrganizationRepositoryImpl,
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
