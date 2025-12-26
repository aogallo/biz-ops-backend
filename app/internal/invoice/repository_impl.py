from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, func, select

from app.internal.invoice.entity import Invoice, InvoiceDetail
from app.internal.invoice.repository import InvoiceRepository
from app.internal.invoice.schema import InvoiceCreate
from app.internal.user.entity import User


class InvoiceRepositoryImpl(InvoiceRepository):
    """
    Implementation of Invoice Repository.
    All queries are automatically scoped to company_id for multi-tenancy.
    """

    def __init__(
        self, session: Session, current_user: User, company_id: UUID
    ) -> None:
        self.db = session
        self.current_user = current_user
        self.company_id = company_id  # Company context for multi-tenancy

    def create_invoice(self, invoice: InvoiceCreate) -> Invoice:
        """Create a new invoice scoped to this company"""
        new_invoice: Invoice = Invoice.model_validate(
            invoice,
            update={
                "company_id": self.company_id,
                "created_by": self.current_user.auth0_user_id,
            },
        )
        self.db.add(new_invoice)
        self.db.commit()
        self.db.refresh(new_invoice)
        return new_invoice

    def get_invoice_by_number(
        self, dte_number: str, serie: str
    ) -> Invoice | None:
        """Get an invoice by DTE number and serie (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id,
            Invoice.dte_number == dte_number,
            Invoice.serie == serie,
        )
        result: Invoice | None = self.db.exec(statement).one_or_none()
        return result

    def get_cancelled_invoices(self) -> list[Invoice]:
        """Get all cancelled invoices (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id, Invoice.is_cancelled
        )
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def get_invoices_by_business_partner(
        self, business_partner_id: UUID
    ) -> list[Invoice]:
        """Get all invoices by business partner (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id,
            Invoice.business_partner_id == business_partner_id,
        )
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def get_invoices_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Invoice]:
        """Get all invoices by date range (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id,
            Invoice.date >= start_date,
            Invoice.date <= end_date,
        )
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def cancel_invoice(self, invoice_id: UUID, cancelled_by: str) -> bool:
        """Cancel an invoice (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id, Invoice.id == invoice_id
        )
        invoice: Invoice | None = self.db.exec(statement).one_or_none()
        if invoice:
            invoice.is_cancelled = True
            invoice.updated_by = cancelled_by
            self.db.commit()
            return True
        return False

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Invoice]:
        """Get all invoices (scoped to company)"""
        statement = (
            select(Invoice)
            .where(Invoice.company_id == self.company_id)
            .order_by(Invoice.date.desc())
            .offset(offset)
            .limit(limit)
        )
        result: list[Invoice] = self.db.exec(statement)._allrows()
        return result

    def add_bulk(self, invoices: list[Invoice]):
        """Add bulk invoices (automatically scoped to company)"""
        # Set company_id and created_by for all invoices
        for invoice in invoices:
            invoice.company_id = self.company_id
            invoice.created_by = self.current_user.auth0_user_id

        self.db.add_all(invoices)
        self.db.commit()
        for invoice in invoices:
            self.db.refresh(invoice)
        return invoices

    def get_invoice_by_serie_and_dte(
        self, serie: str, dte_number: str
    ) -> Invoice | None:
        """Get invoice by serie and dte number (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id,
            Invoice.serie == serie,
            Invoice.dte_number == dte_number,
        )
        result: Invoice | None = self.db.exec(statement).one_or_none()
        return result

    def get_invoice_by_id(self, id: UUID) -> Invoice | None:
        """Get an invoice by ID (scoped to company)"""
        statement = select(Invoice).where(
            Invoice.company_id == self.company_id, Invoice.id == id
        )
        result: Invoice | None = self.db.exec(statement).one_or_none()
        return result

    def get_invoice_details(self, id: UUID) -> list[InvoiceDetail] | None:
        """Get invoice details by invoice ID (scoped to company via invoice)"""
        # First verify invoice belongs to this company
        invoice = self.get_invoice_by_id(id)
        if not invoice:
            return None

        statement = select(InvoiceDetail).where(InvoiceDetail.invoice_id == id)
        result: list[InvoiceDetail] | None = self.db.exec(statement)._allrows()
        return result

    def update_by_id(self, invoice: Invoice):
        """Update an invoice (must belong to this company)"""
        # Verify invoice belongs to this company
        if invoice.company_id != self.company_id:
            return False

        try:
            invoice.updated_by = self.current_user.auth0_user_id
            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)
            return True
        except SQLAlchemyError:
            return False

    def get_count(self) -> int:
        """Get count of invoices (scoped to company)"""
        count_statement = (
            select(func.count())
            .select_from(Invoice)
            .where(Invoice.company_id == self.company_id)
        )
        count: int = self.db.exec(count_statement).one()
        return count
