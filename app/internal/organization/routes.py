from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.organization.entity import Organization
from app.internal.organization.schema import (
    OrganizationCreate,
    OrganizationResponse,
)
from app.internal.organization.service import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["Organization"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.post("", response_model=OrganizationResponse)
def create_organization(
    organization: OrganizationCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = OrganizationService(session=session, current_user=current_user)

    org = Organization(**organization.model_dump())

    return service.create_organization(org)


@router.get("")
def list_organization():
    return []
