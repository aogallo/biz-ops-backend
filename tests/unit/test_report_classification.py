"""Unit tests for report classification aggregation logic."""

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.internal.report.repository_impl import ReportRepositoryImpl
from app.internal.user.entity import User


class TestReportClassificationAggregation:
    """Test sales ledger report aggregates by classification correctly."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        mock = Mock(spec=User)
        mock.auth_id = "auth0|test"
        mock.auth0_user_id = "auth0|test"
        mock.organization_id = uuid4()
        mock.permissions = []
        return mock

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_session, mock_user):
        """Create repository with mocked session."""
        return ReportRepositoryImpl(
            session=mock_session,
            current_user=mock_user,
            company_id=uuid4(),
        )

    def test_aggregation_locally_taxed_goods(self, repository, mock_session):
        """Test invoices classified as local+goods+taxed aggregate correctly."""
        # Mock exec().all() to return invoice data with classification
        mock_result = Mock()
        mock_result.all.return_value = [
            (
                datetime(2024, 1, 1),  # date
                "FACT",  # dte_type
                "A",  # serie
                "001",  # number
                "123",  # nit
                "BusinessPartner",  # name
                100.0,  # subtotal
                12.0,  # iva
                112.0,  # total
                "local",  # origin
                "goods",  # item_type
                "taxed",  # tax_status
            ),
        ]
        mock_session.exec.return_value = mock_result

        entries = repository.get_sales_ledger_entries(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert len(entries) == 1
        assert entries[0].locally_taxed_goods == 100.0
        assert entries[0].locally_taxed_services == 0.0
        assert entries[0].locally_exempt_goods == 0.0
        assert entries[0].locally_exempt_services == 0.0
        assert entries[0].imported_taxed_goods == 0.0
        assert entries[0].imported_taxed_services == 0.0
        assert entries[0].imported_exempt_goods == 0.0
        assert entries[0].imported_exempt_services == 0.0
        assert entries[0].iva == 12.0
        assert entries[0].total == 112.0

    def test_aggregation_imported_services_exempt(
        self, repository, mock_session
    ):
        """Test invoices classified as imported+services+exempt aggregate correctly."""
        mock_result = Mock()
        mock_result.all.return_value = [
            (
                datetime(2024, 1, 1),
                "FACT",
                "A",
                "001",
                "123",
                "BusinessPartner",
                500.0,  # subtotal
                0.0,  # iva
                500.0,  # total
                "imported",  # origin
                "services",  # item_type
                "exempt",  # tax_status
            ),
        ]
        mock_session.exec.return_value = mock_result

        entries = repository.get_sales_ledger_entries(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert len(entries) == 1
        assert entries[0].locally_taxed_goods == 0.0
        assert entries[0].locally_taxed_services == 0.0
        assert entries[0].locally_exempt_goods == 0.0
        assert entries[0].locally_exempt_services == 0.0
        assert entries[0].imported_taxed_goods == 0.0
        assert entries[0].imported_taxed_services == 0.0
        assert entries[0].imported_exempt_goods == 0.0
        assert entries[0].imported_exempt_services == 500.0  # Should be here
        assert entries[0].iva == 0.0
        assert entries[0].total == 500.0

    def test_aggregation_null_classification_shows_zeros(
        self, repository, mock_session
    ):
        """Test invoices with ANY NULL classification field show 0.00 in ALL categories."""
        # Invoice with NULL origin (not yet classified)
        mock_result = Mock()
        mock_result.all.return_value = [
            (
                datetime(2024, 1, 1),
                "FACT",
                "A",
                "001",
                "123",
                "BusinessPartner",
                100.0,  # subtotal
                12.0,  # iva
                112.0,  # total
                None,  # origin (NULL)
                "goods",  # item_type
                "taxed",  # tax_status
            ),
        ]
        mock_session.exec.return_value = mock_result

        entries = repository.get_sales_ledger_entries(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert len(entries) == 1
        # ALL categories should be 0.00 because origin is NULL
        assert entries[0].locally_taxed_goods == 0.0
        assert entries[0].locally_taxed_services == 0.0
        assert entries[0].locally_exempt_goods == 0.0
        assert entries[0].locally_exempt_services == 0.0
        assert entries[0].imported_taxed_goods == 0.0
        assert entries[0].imported_taxed_services == 0.0
        assert entries[0].imported_exempt_goods == 0.0
        assert entries[0].imported_exempt_services == 0.0
        # But iva and total should still be present
        assert entries[0].iva == 12.0
        assert entries[0].total == 112.0

    def test_aggregation_all_eight_categories(self, repository, mock_session):
        """Test that all 8 classification categories can be aggregated."""
        mock_result = Mock()
        mock_result.all.return_value = [
            (
                datetime(2024, 1, 1),
                "FACT",
                "A",
                "001",
                "1",
                "C1",
                100.0,
                12.0,
                112.0,
                "local",
                "goods",
                "taxed",
            ),
            (
                datetime(2024, 1, 2),
                "FACT",
                "A",
                "002",
                "2",
                "C2",
                200.0,
                24.0,
                224.0,
                "local",
                "services",
                "taxed",
            ),
            (
                datetime(2024, 1, 3),
                "FACT",
                "A",
                "003",
                "3",
                "C3",
                300.0,
                0.0,
                300.0,
                "local",
                "goods",
                "exempt",
            ),
            (
                datetime(2024, 1, 4),
                "FACT",
                "A",
                "004",
                "4",
                "C4",
                400.0,
                0.0,
                400.0,
                "local",
                "services",
                "exempt",
            ),
            (
                datetime(2024, 1, 5),
                "FACT",
                "A",
                "005",
                "5",
                "C5",
                500.0,
                60.0,
                560.0,
                "imported",
                "goods",
                "taxed",
            ),
            (
                datetime(2024, 1, 6),
                "FACT",
                "A",
                "006",
                "6",
                "C6",
                600.0,
                72.0,
                672.0,
                "imported",
                "services",
                "taxed",
            ),
            (
                datetime(2024, 1, 7),
                "FACT",
                "A",
                "007",
                "7",
                "C7",
                700.0,
                0.0,
                700.0,
                "imported",
                "goods",
                "exempt",
            ),
            (
                datetime(2024, 1, 8),
                "FACT",
                "A",
                "008",
                "8",
                "C8",
                800.0,
                0.0,
                800.0,
                "imported",
                "services",
                "exempt",
            ),
        ]
        mock_session.exec.return_value = mock_result

        entries = repository.get_sales_ledger_entries(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert len(entries) == 8
        assert entries[0].locally_taxed_goods == 100.0
        assert entries[1].locally_taxed_services == 200.0
        assert entries[2].locally_exempt_goods == 300.0
        assert entries[3].locally_exempt_services == 400.0
        assert entries[4].imported_taxed_goods == 500.0
        assert entries[5].imported_taxed_services == 600.0
        assert entries[6].imported_exempt_goods == 700.0
        assert entries[7].imported_exempt_services == 800.0

    def test_aggregation_mixed_classified_and_unclassified(
        self, repository, mock_session
    ):
        """Test mixed invoices (some classified, some not) - only classified contribute."""
        mock_result = Mock()
        mock_result.all.return_value = [
            # Classified invoice
            (
                datetime(2024, 1, 1),
                "FACT",
                "A",
                "001",
                "123",
                "C1",
                100.0,
                12.0,
                112.0,
                "local",
                "goods",
                "taxed",
            ),
            # Unclassified invoice (NULL origin)
            (
                datetime(2024, 1, 2),
                "FACT",
                "A",
                "002",
                "456",
                "C2",
                200.0,
                24.0,
                224.0,
                None,  # NULL
                "goods",
                "taxed",
            ),
            # Another classified invoice
            (
                datetime(2024, 1, 3),
                "FACT",
                "A",
                "003",
                "789",
                "C3",
                300.0,
                0.0,
                300.0,
                "imported",
                "services",
                "exempt",
            ),
        ]
        mock_session.exec.return_value = mock_result

        entries = repository.get_sales_ledger_entries(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert len(entries) == 3
        # First entry: classified as locally_taxed_goods
        assert entries[0].locally_taxed_goods == 100.0
        assert entries[0].imported_exempt_services == 0.0

        # Second entry: unclassified (all zeros)
        assert entries[1].locally_taxed_goods == 0.0
        assert entries[1].locally_taxed_services == 0.0
        assert entries[1].imported_taxed_goods == 0.0

        # Third entry: classified as imported_exempt_services
        assert entries[2].imported_exempt_services == 300.0
        assert entries[2].locally_taxed_goods == 0.0
