"""Integration tests for report routes."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.internal.account.entity import Account
from app.internal.business_partner.entity import BusinessPartner
from app.internal.company.entity import Company
from app.internal.invoice.entity import Invoice
from app.internal.journal.entity import JournalEntry
from app.internal.user.entity import UserCompanyAccess


@pytest.mark.integration
class TestReportRoutes:
    """Integration tests for /reports endpoints."""

    API_PREFIX = "/api/v1"

    def test_get_general_journal_unauthorized(self, client: TestClient):
        """Test that getting general journal without auth fails."""
        from uuid import uuid4

        company_id = uuid4()
        response = client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal"
        )

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_get_general_journal_empty(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test getting general journal with no data."""
        # Create a company first
        with Session(engine) as session:
            company = Company(
                name="Test Company",
                nit="12345678",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
            )
            session.add(company)
            session.flush()

            # Grant user access to company
            user_access = UserCompanyAccess(
                user_id=test_user.id,
                company_id=company.id,
                role="admin",
                created_by="auth0|test123",
            )
            session.add(user_access)

            session.commit()
            session.refresh(company)
            company_id = company.id

        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal"
        )

        assert response.status_code == 200
        data = response.json()

        assert "entries" in data
        assert "totalDebits" in data
        assert "totalCredits" in data
        assert "count" in data
        assert data["count"] == 0
        assert data["totalDebits"] == 0
        assert data["totalCredits"] == 0

    def test_get_general_journal_with_data(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test getting general journal with sample data."""
        # Create test data
        with Session(engine) as session:
            # Create company
            company = Company(
                name="Test Company 2",
                nit="22222222",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
            )
            session.add(company)
            session.flush()

            # Grant user access to company
            user_access = UserCompanyAccess(
                user_id=test_user.id,
                company_id=company.id,
                role="admin",
                created_by="auth0|test123",
            )
            session.add(user_access)
            session.flush()

            # Create customer
            customer = BusinessPartner(
                name="Test BusinessPartner 2",
                nit="33333333",
                email="test2@example.com",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
                is_customer=True,
                is_vendor=False,
            )
            session.add(customer)
            session.flush()

            # Create accounts
            account_debit = Account(
                account_number="1101",
                name="Cash",
                type="asset",
                organization_id=test_user.organization_id,
            )
            account_credit = Account(
                account_number="4101",
                name="Sales Revenue",
                type="revenue",
                organization_id=test_user.organization_id,
            )
            session.add_all([account_debit, account_credit])
            session.flush()

            if company.id is None or customer.id is None:
                raise ValueError("Mocked data is not configured yet")

            # Create invoice
            invoice = Invoice(
                date=datetime(2024, 1, 15, 12, 0, 0),
                authorization_number="AUTH123",
                dte_type="FACT",
                serie="A",
                dte_number="001",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                invoice_type="income",
                subtotal=100.0,
                total_taxes=12.0,
                total_amount=112.0,
                created_by="auth0|test123",
            )
            session.add(invoice)
            session.flush()

            if (
                invoice.id is None
                or account_credit.id is None
                or account_debit.id is None
            ):
                raise ValueError("Mocked data is not configured yet")

            # Create journal entries
            journal_debit = JournalEntry(
                company_id=company.id,
                invoice_id=invoice.id,
                account_id=account_debit.id,
                debit=112.0,
                credit=0.0,
                description="Cash received from sale",
                created_by="auth0|test123",
            )
            journal_credit = JournalEntry(
                company_id=company.id,
                invoice_id=invoice.id,
                account_id=account_credit.id,
                debit=0.0,
                credit=112.0,
                description="Sales revenue",
                created_by="auth0|test123",
            )
            session.add_all([journal_debit, journal_credit])
            session.commit()

            company_id = company.id

        # Request report
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal"
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "entries" in data
        assert "totalDebits" in data
        assert "totalCredits" in data
        assert "count" in data

        # Check data
        assert data["count"] == 2
        assert data["totalDebits"] == 112.0
        assert data["totalCredits"] == 112.0

        # Check entries
        entries = data["entries"]
        assert len(entries) == 2

        # Check first entry (debit)
        first_entry = entries[0]
        assert "date" in first_entry
        assert "accountNumber" in first_entry
        assert "accountName" in first_entry
        assert "transactionConcept" in first_entry
        assert "debit" in first_entry
        assert "credit" in first_entry
        assert "folioNumber" in first_entry

        # Verify one debit and one credit entry exist
        debit_entries = [e for e in entries if e["debit"] > 0]
        credit_entries = [e for e in entries if e["credit"] > 0]

        assert len(debit_entries) == 1
        assert len(credit_entries) == 1
        assert debit_entries[0]["accountNumber"] == "1101"
        assert credit_entries[0]["accountNumber"] == "4101"

    def test_get_general_journal_with_date_filter(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test getting general journal with date filters."""
        # Create test data with different dates
        with Session(engine) as session:
            # clean database

            company = Company(
                name="Test Company 3",
                nit="44444444",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
            )
            session.add(company)
            session.flush()

            # Grant user access to company
            user_access = UserCompanyAccess(
                user_id=test_user.id,
                company_id=company.id,
                role="admin",
                created_by="auth0|test123",
            )
            session.add(user_access)
            session.flush()

            customer = BusinessPartner(
                name="Test BusinessPartner 3",
                nit="55555555",
                email="test3@example.com",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
                is_customer=True,
                is_vendor=False,
            )
            session.add(customer)
            session.flush()

            account = Account(
                account_number="1102",
                name="Cash",
                type="asset",
                organization_id=test_user.organization_id,
            )
            session.add(account)
            session.flush()

            if company.id is None or customer.id is None:
                raise ValueError("Mocked data is not configured yet")

            # Create invoices with different dates
            invoice1 = Invoice(
                date=datetime(2024, 1, 15),
                authorization_number="AUTH123",
                dte_type="FACT",
                serie="A",
                dte_number="001",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                created_by="auth0|test123",
            )
            invoice2 = Invoice(
                date=datetime(2024, 2, 15),
                authorization_number="AUTH124",
                dte_type="FACT",
                serie="A",
                dte_number="002",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                created_by="auth0|test123",
            )
            session.add_all([invoice1, invoice2])
            session.flush()

            if (
                invoice1.id is None
                or account.id is None
                or invoice2.id is None
            ):
                raise ValueError("Mocked data is not configured yet")

            # Create journal entries
            journal1 = JournalEntry(
                company_id=company.id,
                invoice_id=invoice1.id,
                account_id=account.id,
                debit=100.0,
                credit=0.0,
                description="January entry",
                created_by="auth0|test123",
            )
            journal2 = JournalEntry(
                company_id=company.id,
                invoice_id=invoice2.id,
                account_id=account.id,
                debit=200.0,
                credit=0.0,
                description="February entry",
                created_by="auth0|test123",
            )
            session.add_all([journal1, journal2])
            session.commit()

            company_id = company.id

        # Request report with date filter (only January)
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal"
            f"?start_date=2024-01-01T00:00:00"
            f"&end_date=2024-01-31T23:59:59"
        )

        assert response.status_code == 200
        data = response.json()

        # Should only get January entry
        assert data["count"] == 1
        assert data["totalDebits"] == 100.0
        assert data["entries"][0]["transactionConcept"] == "January entry"

    def test_download_general_journal_pdf_unauthorized(
        self, client: TestClient
    ):
        """Test that getting general journal PDF without auth fails."""
        from uuid import uuid4

        company_id = uuid4()
        response = client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal/pdf"
        )

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_download_general_journal_pdf_success(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test downloading general journal PDF with data."""
        # Create test data
        with Session(engine) as session:
            company = Company(
                name="Test Company 4",
                nit="66666666",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
            )
            session.add(company)
            session.flush()

            # Grant user access to company
            user_access = UserCompanyAccess(
                user_id=test_user.id,
                company_id=company.id,
                role="admin",
                created_by="auth0|test123",
            )
            session.add(user_access)
            session.flush()

            customer = BusinessPartner(
                name="Test BusinessPartner 4",
                nit="77777777",
                email="test4@example.com",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
                is_customer=True,
                is_vendor=False,
            )
            session.add(customer)
            session.flush()

            account_debit = Account(
                account_number="1103",
                name="Cash",
                type="asset",
                organization_id=test_user.organization_id,
            )
            account_credit = Account(
                account_number="4103",
                name="Sales Revenue",
                type="revenue",
                organization_id=test_user.organization_id,
            )
            session.add_all([account_debit, account_credit])
            session.flush()

            if company.id is None or customer.id is None:
                raise ValueError("Mocked data is not created yet")

            invoice = Invoice(
                date=datetime(2024, 3, 15, 12, 0, 0),
                authorization_number="AUTH125",
                dte_type="FACT",
                serie="A",
                dte_number="003",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                invoice_type="income",
                created_by="auth0|test123",
            )
            session.add(invoice)
            session.flush()

            if (
                invoice.id is None
                or account_credit.id is None
                or account_debit.id is None
            ):
                raise ValueError("Mocked data is not created yet")

            journal_debit = JournalEntry(
                company_id=company.id,
                invoice_id=invoice.id,
                account_id=account_debit.id,
                debit=200.0,
                credit=0.0,
                description="Test PDF entry",
                created_by="auth0|test123",
            )
            journal_credit = JournalEntry(
                company_id=company.id,
                invoice_id=invoice.id,
                account_id=account_credit.id,
                debit=0.0,
                credit=200.0,
                description="Test PDF revenue",
                created_by="auth0|test123",
            )
            session.add_all([journal_debit, journal_credit])
            session.commit()

            company_id = company.id

        # Request PDF
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal/pdf"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        assert (
            "general_journal_company"
            in response.headers["Content-Disposition"]
        )

        # Verify PDF content starts with PDF magic bytes
        assert response.content[:4] == b"%PDF"

    def test_download_general_journal_pdf_with_date_filter(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test downloading PDF with date filters."""
        # Create test data with different dates
        with Session(engine) as session:
            company = Company(
                name="Test Company 5",
                nit="88888888",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
            )
            session.add(company)
            session.flush()

            # Grant user access to company
            user_access = UserCompanyAccess(
                user_id=test_user.id,
                company_id=company.id,
                role="admin",
                created_by="auth0|test123",
            )
            session.add(user_access)
            session.flush()

            customer = BusinessPartner(
                name="Test BusinessPartner 5",
                nit="99999999",
                email="test5@example.com",
                organization_id=test_user.organization_id,
                created_by="auth0|test123",
                is_customer=True,
                is_vendor=False,
            )
            session.add(customer)
            session.flush()

            account = Account(
                account_number="1104",
                name="Cash",
                type="asset",
                organization_id=test_user.organization_id,
            )
            session.add(account)
            session.flush()

            if company.id is None or customer.id is None:
                raise ValueError("Mocked data is not configured yet")

            # Create invoices with different dates
            invoice1 = Invoice(
                date=datetime(2024, 3, 15),
                authorization_number="AUTH126",
                dte_type="FACT",
                serie="A",
                dte_number="004",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                created_by="auth0|test123",
            )
            invoice2 = Invoice(
                date=datetime(2024, 4, 15),
                authorization_number="AUTH127",
                dte_type="FACT",
                serie="A",
                dte_number="005",
                sat_issuer_name="Test Issuer",
                sat_receiver_name="Test Receiver",
                company_id=company.id,
                business_partner_id=customer.id,
                created_by="auth0|test123",
            )
            session.add_all([invoice1, invoice2])
            session.flush()

            if (
                invoice1.id is None
                or account.id is None
                or invoice2.id is None
            ):
                raise ValueError("Mocked data is not configured yet")

            # Create journal entries
            journal1 = JournalEntry(
                company_id=company.id,
                invoice_id=invoice1.id,
                account_id=account.id,
                debit=300.0,
                credit=0.0,
                description="March entry",
                created_by="auth0|test123",
            )
            journal2 = JournalEntry(
                company_id=company.id,
                invoice_id=invoice2.id,
                account_id=account.id,
                debit=400.0,
                credit=0.0,
                description="April entry",
                created_by="auth0|test123",
            )
            session.add_all([journal1, journal2])
            session.commit()

            company_id = company.id

        # Request PDF with date filter (only March)
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal/pdf"
            f"?start_date=2024-03-01T00:00:00"
            f"&end_date=2024-03-31T23:59:59"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"

        # Verify filename contains date range
        assert "20240301_20240331" in response.headers["Content-Disposition"]

    def test_download_general_journal_pdf_company_not_found(
        self,
        authenticated_client: TestClient,
    ):
        """Test PDF download with non-existent company."""
        from uuid import uuid4

        company_id = uuid4()
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies/{company_id}/reports/general-journal/pdf"
        )

        assert response.status_code == 404
        assert (
            f"Company with identifier '{company_id}' not found"
            in response.json()["detail"]
        )
