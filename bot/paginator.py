"""Paginator."""
from telegram import InlineKeyboardButton

from display_data import buttons as btn


class Paginator:
    """Paginator."""

    def __init__(self, items: dict, callback_pattern: str,
                 items_per_page: int = 5):
        """Initialize class data."""
        self.items = list(items.items())
        self.items_per_page = items_per_page
        self.callback_pattern = callback_pattern
        self.total_pages = (len(items) + items_per_page - 1) // items_per_page

    def get_page(self, page: int) -> list:
        """Get pages item."""
        start = (page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def create_pagination_buttons(self, current_page) -> list:
        """Return pagination buttons."""
        buttons = []
        if self.total_pages < 2:
            return []
        if current_page > 1:
            buttons.append(InlineKeyboardButton(
                btn.BACK_PAGINATOR_BUTTON,
                callback_data=f'{self.callback_pattern}{current_page-1}'))
        buttons.append(InlineKeyboardButton(
            str(current_page),
            callback_data=f'{self.callback_pattern}{current_page}'))
        if current_page < self.total_pages:
            buttons.append(InlineKeyboardButton(
                btn.FORWARD_PAGINATOR_BUTTON,
                callback_data=f'{self.callback_pattern}{current_page+1}'))
        return buttons
