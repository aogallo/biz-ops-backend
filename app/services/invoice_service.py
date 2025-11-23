from io import BytesIO

import pandas as pd

from app.domain.entities.user import User
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)
from app.schemas.invoice_schema import InvoiceRowSchema


class InvoiceService:
    """Service for managing invoices."""

    def __init__(self, current_user: User) -> None:
        self.customer_repo = CustomerRepositoryImpl(current_user)
        self.invoice_repo = CustomerRepositoryImpl(current_user)
        self.errors: list[dict] = []

    def list_all_invoices(self):
        return self.customer_repo.get_all_customers()

    def process_file(self, file_bytes: bytes):
        df = pd.read_excel(BytesIO(file_bytes))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        CHUNK_SIZE = 1000  # Process rows in batches

        # Process in chunks for memory efficiency
        for chunk_start in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[chunk_start : chunk_start + CHUNK_SIZE]
            validated_rows = self._validate_chunk(chunk, chunk_start)

            if validated_rows:
                self._process_validated_rows(validated_rows)

    def _validate_chunk(self, chunk: pd.DataFrame, offset: int):
        """Validate rows using Pydantic, collect errors."""
        validated = []

        for idx, row in chunk.iterrows():
            row_num = offset + idx + 2  # +2 for Excel row (1-indexed + header)
            try:
                # validated_row = InvoiceRowSchema(**row.to_dict())
                validated.append(row.to_dict())
            except Exception as e:
                self.errors.append(
                    {
                        "row": row_num,
                        "error": str(e),
                        "data": {k: str(v) for k, v in row.to_dict().items()},
                    }
                )

        return validated

    def _process_validated_rows(self, rows: list[InvoiceRowSchema]) -> None:
        """Process validated rows: users, invoices, details."""

        # 1. Batch get/create users
        emails = list({r.user_email for r in rows})
        user_map = self._get_or_create_users(rows, emails)

        # 2. Group rows by invoice
        # invoices_grouped = defaultdict(list)
        # for row in rows:
        #     key = (row.user_email, row.invoice_number)
        #     invoices_grouped[key].append(row)

        # 3. Check existing invoices (for duplicate handling)
        # invoice_numbers = [r.invoice_number for r in rows]
        # existing_invoices = {
        #     inv.invoice_number: inv
        #     for inv in self.db.query(Invoice)
        #     .filter(Invoice.invoice_number.in_(invoice_numbers))
        #     .all()
        # }

        # 4. Create invoices and details
        # for (email, inv_number), detail_rows in invoices_grouped.items():
        #     if inv_number in existing_invoices:
        #         self.stats["invoices_skipped"] += 1
        #         continue
        #
        #     user = user_map[email]
        #     first_row = detail_rows[0]
        #
        #     invoice = Invoice(
        #         user_id=user.id,
        #         invoice_number=inv_number,
        #         invoice_date=first_row.invoice_date,
        #     )
        #     self.db.add(invoice)
        #     self.db.flush()
        #     self.stats["invoices_created"] += 1
        #
        #     # Bulk insert details
        #     details = [
        #         InvoiceDetail(
        #             invoice_id=invoice.id,
        #             product=row.product,
        #             quantity=row.quantity,
        #             unit_price=row.unit_price,
        #             total=row.quantity * row.unit_price,
        #         )
        #         for row in detail_rows
        #     ]
        # self.db.bulk_save_objects(details)

    def _get_or_create_users(
        self, rows: list[InvoiceRowSchema], emails: list[str]
    ) -> dict:
        """Batch fetch existing users, create missing ones."""

        # Fetch existing
        existing = {
            u.email: u
            for u in self.db.query(User).filter(User.email.in_(emails)).all()
        }
        self.stats["users_existing"] += len(existing)

        # Find missing emails
        email_to_name = {r.user_email: r.user_name for r in rows}
        missing_emails = set(emails) - set(existing.keys())

        # Bulk create missing users
        if missing_emails:
            new_users = [
                User(email=email, name=email_to_name[email])
                for email in missing_emails
            ]
            self.db.bulk_save_objects(new_users, return_defaults=True)
            self.db.flush()

            # Refresh to get IDs
            for user in new_users:
                existing[user.email] = user
            self.stats["users_created"] += len(new_users)

        return existing
