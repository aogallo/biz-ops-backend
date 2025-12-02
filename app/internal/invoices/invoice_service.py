import logging
from datetime import datetime
from io import BytesIO

import pandas as pd
from fastapi import HTTPException, status
from sqlmodel import Session

from app.domain.entities.company import Company
from app.domain.entities.customer import Customer
from app.domain.entities.user import User
from app.infrastructure.repositories.company_repostiory_impl import (
    CompanyRepositoryImpl,
)
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)
from app.internal.accounts.account_respository_impl import (
    AccountRepositoryImpl,
)
from app.internal.invoices.invoice_detail_entity import InvoiceDetail
from app.internal.invoices.invoice_entity import Invoice, InvoiceUpdate
from app.internal.invoices.invoice_repository_impl import InvoiceRepositoryImpl
from app.internal.invoices.invoice_schema import InvoiceRowSchema
from app.utils.dates import normalize_datetime

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for managing invoices."""

    def __init__(self, session: Session, current_user: User) -> None:
        self.customer_repo = CustomerRepositoryImpl(session, current_user)
        self.company_repo = CompanyRepositoryImpl(session, current_user)
        self.invoice_repo = InvoiceRepositoryImpl(session)
        self.accont_repo = AccountRepositoryImpl(
            session=session, current_user=current_user
        )
        self.errors: list[dict] = []
        self.current_user = current_user

    def list_all_invoices(self):
        return self.invoice_repo.get_all()

    def process_file(self, file_bytes: bytes):
        try:
            df = pd.read_excel(BytesIO(file_bytes))
            df.rename(
                columns={
                    "Fecha de emisión": "date",
                    "Número de Autorización": "authorization_number",
                    "Tipo de DTE (nombre)": "dte_type",
                    "Serie": "serie",
                    "Número del DTE": "dte_number",
                    "Clasificación emisor": "clasificacion_emisor",
                    "Exportación": "exportation",
                    "NIT del emisor": "company_nit",
                    "Nombre completo del emisor": "company_name",
                    "Código de establecimiento": "company_code",
                    "Nombre del establecimiento": "company_description",
                    "ID del receptor": "customer_nit",
                    "Nombre completo del receptor": "customer_name",
                    "NIT del Certificador": "certificator_nit",
                    "Nombre completo del Certificador": "certificator_name",
                    "Estado": "state",
                    "Moneda": "money",
                    "Gran Total (Moneda Original)": "total",
                    "IVA (monto de este impuesto)": "iva",
                    "Marca de anulado": "is_voided",
                    "Fecha de anulación": "voided_date",
                    "Petróleo (monto de este impuesto)": "petroleum",
                    "Turismo Hospedaje (monto de este impuesto)": "hotel",
                    "Turismo Pasajes (monto de este impuesto)": "tickets",
                    "Timbre de Prensa (monto de este impuesto)": "press_stamp",
                    "Bomberos (monto de este impuesto)": "firefigthers",
                    "Tasa Municipal (monto de este impuesto)": (
                        "municipal_tax"
                    ),
                    "Bebidas alcohólicas (monto de este impuesto)": (
                        "alcoholic_tax"
                    ),
                    "Tabaco (monto de este impuesto)": "tobacco_tax",
                    "Cemento (monto de este impuesto)": "cement_tax",
                    "Bebidas no Alcohólicas (monto de este impuesto)": (
                        "no_alcoholic_tax"
                    ),
                    "Tarifa Portuaria (monto de este impuesto)": (
                        "port_tariff_tax"
                    ),
                },
                inplace=True,
            )

            CHUNK_SIZE = 1000  # Process rows in batches

            response = ""
            # Process in chunks for memory efficiency
            for chunk_start in range(0, len(df), CHUNK_SIZE):
                chunk = df.iloc[(chunk_start) : (chunk_start + CHUNK_SIZE)]
                validated_rows = self._validate_chunk(chunk, chunk_start)

                if validated_rows:
                    response = self._process_validated_rows(validated_rows)

            return response

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            ) from e

    def _validate_chunk(self, chunk: pd.DataFrame, offset: int):
        """Validate rows using Pydantic, collect errors."""
        validated: list[InvoiceRowSchema] = []

        for _, row in chunk.iterrows():
            try:
                validated_row = InvoiceRowSchema.model_validate(row.to_dict())
                validated.append(validated_row)
            except Exception as e:
                logger.error(
                    "Failing creating the Invoice Row File %s", str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="There are some lines do not match with the expected values",
                ) from e

        return validated

    def _get_unique_companies(
        self, invoices: list[InvoiceRowSchema]
    ) -> list[dict]:
        """Extract unique companies from invoice rows"""
        companies = {}

        for invoice in invoices:
            if invoice.company_nit not in companies:
                companies[invoice.company_nit] = {
                    "nit": invoice.company_nit,
                    "name": invoice.company_name,
                }

        return list(companies.values())

    def _get_unique_customers(self, invoices: list[InvoiceRowSchema]):
        """Extract unique customers from invoice rows"""
        customers = {
            invoice.customer_nit: {
                "nit": invoice.customer_nit,
                "name": invoice.customer_name,
            }
            for invoice in invoices
        }

        return list(customers.values())

    def _create_missing_companies(self, rows: list[InvoiceRowSchema]):
        """Find and create companies that don't exist in the database"""
        # 1. Batch get/create users
        unique_companies = self._get_unique_companies(rows)

        # Get existing company NITs from database
        existing_companies = self.company_repo.get_companies_by_nit(
            unique_companies
        )
        existing_nits_set = {c.nit for c in existing_companies}

        # Find companies that don't exist
        new_companies = []
        for company_data in unique_companies:
            if company_data["nit"] not in existing_nits_set:
                new_company = Company(
                    nit=company_data["nit"],
                    name=company_data["name"],
                    created_by=self.current_user.auth_id,
                )
                new_companies.append(new_company)

        # Bulk insert new companies
        if new_companies:
            self.company_repo.add_bulk(new_companies)

            logger.info("Created %d new companies", len(new_companies))
        else:
            logger.info("No new companies to create")

        return new_companies + existing_companies

    def _create_missing_customers(self, invoices: list[InvoiceRowSchema]):
        """Find and create customers that do not exist in the database"""
        unique_customers = self._get_unique_customers(invoices)

        existing_customers = self.customer_repo.get_customers_by_nit(
            unique_customers
        )
        existing_nits_set = {c.nit for c in existing_customers}

        # Create missing customers
        new_customers = []
        for customer_data in unique_customers:
            if customer_data["nit"] not in existing_nits_set:
                new_customer = Customer(
                    nit=customer_data["nit"],
                    name=customer_data["name"],
                    email=None,
                    created_by=self.current_user.auth_id,
                )
                new_customers.append(new_customer)

        if new_customers:
            self.customer_repo.add_bulk(new_customers)

            logger.info("Created %d new customers", len(new_customers))
        else:
            logger.info("No new customers to create")

        return existing_customers + new_customers

    def _process_validated_rows(self, rows: list[InvoiceRowSchema]):
        """Process validated rows: companies, invoices, details."""
        existing_companies = self._create_missing_companies(rows)
        customers = self._create_missing_customers(rows)

        # Create NIT-to-ID lookup dictionaries
        company_nit_to_id = {
            company.nit: company.id for company in existing_companies
        }
        customer_nit_to_id = {
            customer.nit: customer.id for customer in customers
        }

        logger.info(
            "Created mappings for %d companies and %d customers",
            len(company_nit_to_id),
            len(customer_nit_to_id),
        )

        # Create invoices with details
        invoices_to_create = []
        for row in rows:
            # Map NITs to IDs
            company_id = company_nit_to_id.get(row.company_nit)
            customer_id = customer_nit_to_id.get(row.customer_nit)

            if not company_id or not customer_id:
                logger.warning(
                    "Skipping row - missing mapping: "
                    "company_nit=%s, customer_nit=%s",
                    row.company_nit,
                    row.customer_nit,
                )
                continue

            invoice = self.invoice_repo.get_invoice_by_serie_and_dte(
                dte_number=row.dte_number, serie=row.serie
            )

            if invoice is not None:
                logger.info(
                    "Invoice already exist serie: %s, dte_number: %s",
                    row.serie,
                    row.dte_number,
                )
                continue

            # Parse date from string
            # time data '2025-11-20T15:01:19' does match format '%Y-%m-%d %H:%M:%S'
            invoice_date = normalize_datetime(row.date)

            # Create invoice header
            invoice = Invoice(
                date=invoice_date,
                authorization_number=row.authorization_number,
                dte_type=row.dte_type,
                serie=row.serie,
                dte_number=str(row.dte_number),
                company_id=company_id,
                customer_id=customer_id,
                currency=row.money,
                state=row.state,
                is_cancelled=row.is_voided,
                cancelled_date=(
                    datetime.strptime(row.voided_date, "%Y-%m-%d %H:%M:%S")
                    if row.voided_date and row.voided_date.strip()
                    else None
                ),
                created_by=self.current_user.auth_id,
            )

            # Create invoice detail (one per row based on file structure)
            detail = InvoiceDetail(
                invoice=invoice,
                product_name="Invoice Item",  # Generic, no product details
                quantity=1.0,
                unit_price=row.total - row.iva,  # Total includes IVA
                iva=row.iva,
                petroleo=row.petroleum,
                turismo_hospedaje=row.hotel,
                turismo_pasajes=row.tickets,
                timbre_prensa=row.press_stamp,
                bomberos=row.firefigthers,
                tasa_municipal=row.municipal_tax,
                bebidas_alcoholicas=row.alcoholic_tax,
                tabaco=row.tobacco_tax,
                cemento=row.cement_tax,
                bebidas_no_alcoholicas=row.no_alcoholic_tax,
                tarifa_portuaria=row.port_tariff_tax,
                created_by=self.current_user.auth_id,
            )

            # Calculate detail totals
            detail.calculate_totals()

            # Add detail to invoice
            invoice.details = [detail]

            # Calculate invoice totals
            invoice.calculate_totals()

            invoices_to_create.append(invoice)

        # Bulk insert invoices with details
        if invoices_to_create:
            self._bulk_insert_invoices(invoices_to_create)
            logger.info(
                "Created %d invoices with details", len(invoices_to_create)
            )
            return "Created %d invoices with details", len(invoices_to_create)
        else:
            logger.info("No invoices to create")
            return "No invoices to create"

    def _bulk_insert_invoices(self, invoices: list[Invoice]):
        """Bulk insert invoices with their details"""
        self.invoice_repo.add_bulk(invoices)
        logger.info("Invoices created successfully: %d", len(invoices))

    def get_invoice_by_id(self, id: int):
        invoice = self.invoice_repo.get_invoice_by_id(id)

        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )

        return invoice

    def get_invoice_deatils(self, id: int):
        details = self.invoice_repo.get_invoice_details(id)

        return details

    def update_invoice_by_id(self, id: int, invoice: InvoiceUpdate):
        db_invoice = self.invoice_repo.get_invoice_by_id(id)

        if db_invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not exists",
            )

        db_account = self.accont_repo.get_by_id(id)

        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not exists",
            )

        invoice_data = invoice.model_dump(exclude_unset=True)
        db_invoice.sqlmodel_update(invoice_data)
        return self.invoice_repo.update_by_id(db_invoice)
