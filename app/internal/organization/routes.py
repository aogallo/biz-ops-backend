from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.organization.entity import Organization
from app.internal.organization.schema import (
    OrganizationCreate,
    OrganizationListResponse,
    OrganizationResponse,
)
from app.internal.organization.service import OrganizationService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

router = APIRouter(
    prefix="/admin/organizations",
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


@router.get("", response_model=OrganizationListResponse)
def list_organization(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        offset = calculate_offset(page=page, page_size=limit)
        service = OrganizationService(
            session=session,
            current_user=current_user,
        )

        result = service.get_organizations(
            offset=offset,
            limit=limit,
        )

        pagination = PaginationResponse(
            total=result.count,
            page_size=limit,
            page_index=page - 1,
        )

        return OrganizationListResponse(
            organizations=[
                OrganizationResponse.model_validate(organization)
                for organization in result.organizations
            ],
            pagination=pagination,
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
