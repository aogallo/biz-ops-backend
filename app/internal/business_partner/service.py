from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.internal.business_partner.entity import BusinessPartnerCreate
from app.internal.business_partner.repository_impl import (
    BusinessPartnerRepositoryImpl,
)
from app.internal.business_partner.service_schemas import (
    BusinessPartnerListServiceResponse,
)
from app.internal.user.entity import User


class BusinessPartnerService:
    """Service for managing business partners (organization-scoped)."""

    def __init__(
        self,
        session: Session,
        current_user: User,
        organization_id: UUID | None = None,
    ) -> None:
        # Use provided organization_id or extract from current_user
        org_id = organization_id or current_user.organization_id
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization",
            )
        self.repository = BusinessPartnerRepositoryImpl(
            session, current_user, org_id
        )

    def create_customer(self, customer: BusinessPartnerCreate):
        """
        Create a new customer.
        Raises error if customer with same email exists.
        """
        existed_customer = self.repository.get_by_nit(customer.nit)

        if existed_customer is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="BusinessPartner already exists",
            )

        return self.repository.create(customer)

    def list_all_customers(
        self, offset: int, limit: int
    ) -> BusinessPartnerListServiceResponse:
        """
        List all business partners with pagination (organization-scoped).

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            BusinessPartnerListServiceResponse: Validated response with count and
                customers

        Raises:
            HTTPException: If database query fails
        """
        customers = self.repository.get_all(offset=offset, limit=limit)
        count = self.repository.get_count()

        return BusinessPartnerListServiceResponse(
            count=count, customers=customers
        )
