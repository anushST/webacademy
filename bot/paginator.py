"""Paginator."""


class Paginator():
    """Paginator."""

    def __init__(self, data: list, page_size: int) -> None:
        """Initialize data."""
        self.data = data
        self.page_size = page_size
        self.data_length = len(data)
        self.pages_count = self.data_length // page_size
        if (self.data_length / page_size > self.pages_count):
            self.pages_count += 1

    def paginate(page: int = 1):
        """Paginate data and return."""


    def get_pagination(page: int = 1) -> None:
        """Return paginated data."""
