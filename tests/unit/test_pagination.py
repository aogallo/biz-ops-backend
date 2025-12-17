"""Unit tests for pagination utilities."""

from app.utils.pagination import calculate_offset


class TestCalculateOffset:
    """Test offset calculation for pagination."""

    def test_first_page_offset_is_zero(self):
        """Test that page 1 returns offset 0."""
        assert calculate_offset(page=1, page_size=10) == 0
        assert calculate_offset(page=1, page_size=25) == 0
        assert calculate_offset(page=1, page_size=100) == 0

    def test_second_page_offset(self):
        """Test that page 2 calculates correct offset."""
        assert calculate_offset(page=2, page_size=10) == 10
        assert calculate_offset(page=2, page_size=25) == 25
        assert calculate_offset(page=2, page_size=100) == 100

    def test_third_page_offset(self):
        """Test that page 3 calculates correct offset."""
        assert calculate_offset(page=3, page_size=10) == 20
        assert calculate_offset(page=3, page_size=25) == 50
        assert calculate_offset(page=3, page_size=100) == 200

    def test_large_page_number(self):
        """Test offset calculation for large page numbers."""
        assert calculate_offset(page=100, page_size=10) == 990
        assert calculate_offset(page=50, page_size=20) == 980
        assert calculate_offset(page=10, page_size=50) == 450

    def test_invalid_page_number_defaults_to_first_page(self):
        """Test that page < 1 defaults to page 1."""
        assert calculate_offset(page=0, page_size=10) == 0
        assert calculate_offset(page=-1, page_size=10) == 0
        assert calculate_offset(page=-100, page_size=25) == 0

    def test_default_page_size(self):
        """Test that default page size is 10."""
        assert calculate_offset(page=1) == 0
        assert calculate_offset(page=2) == 10
        assert calculate_offset(page=5) == 40
