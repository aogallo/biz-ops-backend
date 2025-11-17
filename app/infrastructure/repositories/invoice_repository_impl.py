from typing import override

from fastapi import Depends
from sqlmodel import Session

from app.domain.entities.invoice import Invoice, InvoiceCreate
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.infrastructure.database import get_current_session


class InvoiceRepositoryImpl(InvoiceRepository):
    """Implementation of Invoice Repository Interface."""

    def __init__(
        self, session: Session | None = Depends(get_current_session)
    ) -> None:
        self.db = session

    @override
    def create_invoice(self, invoice: InvoiceCreate) -> Invoice:
        pass
