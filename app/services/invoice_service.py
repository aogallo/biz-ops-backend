import logging
from io import BytesIO

import pandas as pd

from app.domain.entities.company import Company
from app.domain.entities.customer import Customer
from app.domain.entities.user import User
from app.infrastructure.repositories.company_repostiory_impl import (
    CompanyRepositoryImpl,
)
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)
from app.schemas.invoice_schema import InvoiceRowSchema

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for managing invoices."""

    def __init__(self, current_user: User) -> None:
        self.customer_repo = CustomerRepositoryImpl(current_user)
        self.company_repo = CompanyRepositoryImpl(current_user)
        self.invoice_repo = CustomerRepositoryImpl(current_user)
        self.errors: list[dict] = []
        self.current_user = current_user

    def list_all_invoices(self):
        return self.customer_repo.get_all_customers()

    def process_file(self, file_bytes: bytes):
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
                "Tasa Municipal (monto de este impuesto)": "municipal_tax",
                "Bebidas alcohólicas (monto de este impuesto)": "alcoholic_tax",
                "Tabaco (monto de este impuesto)": "tobacco_tax",
                "Cemento (monto de este impuesto)": "cement_tax",
                "Bebidas no Alcohólicas (monto de este impuesto)": "no_alcoholic_tax",
                "Tarifa Portuaria (monto de este impuesto)": "port_tariff_tax",
            },
            inplace=True,
        )

        CHUNK_SIZE = 1000  # Process rows in batches

        # Process in chunks for memory efficiency
        for chunk_start in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[chunk_start : chunk_start + CHUNK_SIZE]
            validated_rows = self._validate_chunk(chunk, chunk_start)

            if validated_rows:
                self._process_validated_rows(validated_rows)

    def _validate_chunk(self, chunk: pd.DataFrame, offset: int):
        """Validate rows using Pydantic, collect errors."""
        validated: list[InvoiceRowSchema] = []

        for idx, row in chunk.iterrows():
            row_num = (
                offset + int(idx) + 2
            )  # +2 for Excel row (1-indexed + header)

            try:
                validated_row = InvoiceRowSchema.model_validate(row.to_dict())
                validated.append(validated_row)
            except Exception as e:
                raise Exception(str(e))
                self.errors.append(
                    {
                        "row": row_num,
                        "error": str(e),
                        "data": {k: str(v) for k, v in row.to_dict().items()},
                    }
                )

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
        existing_nits = self.company_repo.get_companies_nits()
        existing_nits_set = set(existing_nits)

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

            logger.info("Created $d new companies", len(new_companies))
        else:
            logger.info("No new companies to create")

    def _create_missing_customers(self, invoices: list[InvoiceRowSchema]):
        """Find and create customers that do not exist in the database"""
        unique_customers = self._get_unique_customers(invoices)

        existing_nits = self.customer_repo.get_customer_nits()
        existing_nits_set = set(existing_nits)

        # Create missing customers
        new_customers = []
        for customer_data in unique_customers:
            if customer_data["nit"] not in existing_nits_set:
                new_customer = Customer(
                    nit=customer_data["nit"],
                    name=customer_data["name"],
                    created_by=self.current_user.auth_id,
                )
                new_customers.append(new_customer)

        if new_customers:
            self.customer_repo.add_bulk(new_customers)

            logger.info("Created $d new customers", len(new_customers))
        else:
            logger.info("No new customers to create")

    def _process_validated_rows(self, rows: list[InvoiceRowSchema]) -> None:
        """Process validated rows: companies, invoices, details."""
        existing_companies = self._create_missing_companies(rows)
        customers = self._create_missing_customers(rows)
