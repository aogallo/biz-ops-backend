from uuid import UUID

from sqlmodel import Session, col, func, select

from app.internal.business_partner.entity import (
    BusinessPartner,
    BusinessPartnerCreate,
)
from app.internal.business_partner.repository import BusinessPartnerRepository
from app.internal.user.entity import User


class BusinessPartnerRepositoryImpl(BusinessPartnerRepository):
    """
    Implementation of Business Partner Repository.
    All queries are automatically scoped to organization_id for multi-tenancy.
    BusinessPartners are organization-scoped (shared across companies).
    """

    def __init__(
        self, session: Session, current_user: User, organization_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.organization_id = (
            organization_id  # Organization context for multi-tenancy
        )

    def create(
        self, business_partner_create: BusinessPartnerCreate
    ) -> BusinessPartner:
        """Create a new business partner scoped to this organization"""
        business_partner: BusinessPartner = BusinessPartner.model_validate(
            business_partner_create,
            update={
                "organization_id": self.organization_id,
                "created_by": self.current_user.auth0_user_id,
            },
        )
        self.db.add(business_partner)
        self.db.commit()
        self.db.refresh(business_partner)
        return business_partner

    def get_all(self, offset: int, limit: int) -> list[BusinessPartner]:
        """Get all business partners (scoped to organization)"""
        statement = (
            select(BusinessPartner)
            .where(BusinessPartner.organization_id == self.organization_id)
            .offset(offset)
            .limit(limit)
        )
        result: list[BusinessPartner] = list(self.db.exec(statement))
        return result

    def get_by_id(self, id: UUID) -> BusinessPartner | None:
        """Get a business partner by ID (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            BusinessPartner.id == id,
        )
        result: BusinessPartner | None = self.db.exec(statement).one_or_none()
        return result

    def get_by_email(self, email: str) -> BusinessPartner | None:
        """Get business partner by email (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            BusinessPartner.email == email,
        )
        result: BusinessPartner | None = self.db.exec(statement).one_or_none()
        return result

    def get_by_name(self, name: str) -> BusinessPartner | None:
        """Get business partner by name (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            BusinessPartner.name == name,
        )
        result: BusinessPartner | None = self.db.exec(statement).one_or_none()
        return result

    def get_names(self, names: list[str]) -> list[BusinessPartner]:
        """Get business partners by names (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            col(BusinessPartner.name).in_(names),
        )
        results: list[BusinessPartner] = list(self.db.exec(statement).all())
        return results

    def get_by_nits(self, nits: list[str]) -> list[BusinessPartner]:
        """Get existing business partners by NITs (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            col(BusinessPartner.nit).in_(nits),
        )
        result: list[BusinessPartner] = self.db.exec(statement)._allrows()
        return list(result)

    def add_bulk(self, business_partners: list[BusinessPartner]):
        """Add bulk business partners (automatically scoped to organization)"""
        # Set organization_id and created_by for all business partners
        for partner in business_partners:
            partner.organization_id = self.organization_id
            partner.created_by = self.current_user.auth0_user_id

        self.db.add_all(business_partners)
        self.db.commit()
        for partner in business_partners:
            self.db.refresh(partner)

    def get_by_nit(self, nit: str) -> BusinessPartner | None:
        """Get business partner by NIT (scoped to organization)"""
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            BusinessPartner.nit == nit,
        )
        result: BusinessPartner | None = self.db.exec(
            statement
        ).one_or_none()
        return result

    def get_or_create_by_nit(
        self,
        nit: str,
        name: str,
        is_vendor: bool = False,
        is_customer: bool = False,
    ) -> BusinessPartner:
        """
        Get or create business partner by NIT (scoped to organization).
        Used for SAT invoice upload processing.
        """
        statement = select(BusinessPartner).where(
            BusinessPartner.organization_id == self.organization_id,
            BusinessPartner.nit == nit,
        )
        partner = self.db.exec(statement).first()

        if not partner:
            partner = BusinessPartner(
                organization_id=self.organization_id,
                nit=nit,
                name=name,
                is_vendor=is_vendor,
                is_customer=is_customer,
                created_by=self.current_user.auth0_user_id,
            )
            self.db.add(partner)
            self.db.commit()
            self.db.refresh(partner)

        return partner

    def get_count(self) -> int:
        """Get count of business partners (scoped to organization)"""
        count_statement = (
            select(func.count())
            .select_from(BusinessPartner)
            .where(BusinessPartner.organization_id == self.organization_id)
        )
        count: int = self.db.exec(count_statement).one()
        return count
