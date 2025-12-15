"""Pagination utility functions."""


def calculate_offset(page: int, page_size: int = 10) -> int:
    """
    Calculate database offset from page number.

    Args:
        page: Page number (1-indexed)
        page_size: Number of records per page

    Returns:
        Offset value for database query (0-indexed)

    Examples:
        >>> calculate_offset(page=1, page_size=10)
        0
        >>> calculate_offset(page=2, page_size=10)
        10
        >>> calculate_offset(page=3, page_size=10)
        20
        >>> calculate_offset(page=1, page_size=25)
        0
        >>> calculate_offset(page=2, page_size=25)
        25
    """
    if page < 1:
        page = 1

    return (page - 1) * page_size
