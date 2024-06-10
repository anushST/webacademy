"""Database queries."""
import sqlite3
from typing import Any

from .constants import DATABASE
from .exceptions import (FieldDoesNotExistError, ObjectDoesNotExistError,
                         ValidationError)


USERS_TABLE_FIELDS = ('chat_id', 'lang', 'main_message_id',
                      'course_message_info_id',)


def create_users_table() -> None:
    """Note: Run once, to create table."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL,
                main_message_id INTEGER,
                course_info_message_id INTEGER
            )
        ''')


def create_user(chat_id: int, lang: str) -> None:
    """Record user at database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (chat_id, lang)
            VALUES (?, ?)
            ''', (chat_id, lang))


class User:
    """Users' records manager.

    chat_id: int - User's chat_id
    """

    def __init__(self, chat_id: int) -> None:
        """Initialize class data."""
        self.chat_id = chat_id
        self.database_path = DATABASE
        self._ensure_object_exists(chat_id)

    def _ensure_object_exists(self, pk) -> None:
        """Ensure object exists."""
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE chat_id = ?',
                           (pk,))
            result = cursor.fetchone()
        if result is None:
            raise ObjectDoesNotExistError(
                'Object with this chat_id does not exist.')

    def ensure_field_exists(self, field: str) -> bool:
        """Ensure field exists, if no raise FieldDoesNotExistsError.

        This step does to prevent SQL-injections.
        """
        if field in USERS_TABLE_FIELDS:
            return True
        raise FieldDoesNotExistError(f'Field "{field}" does not exist in db.')

    def validate_field_name(self, field_name) -> None:
        """Validate field name parametr."""
        if field_name == 'chat_id':
            raise ValidationError('Name "chat_id" does not allowed to edit.')

    def get_field(self, field_name) -> Any:
        """Get field by field name."""
        self.ensure_field_exists(field_name)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT {field_name} FROM users WHERE chat_id = ?',
                           (self.chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def edit_field(self, field_name, new_value) -> Any:
        """Edit field by field name."""
        self.ensure_field_exists(field_name)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            self.validate_field_name(field_name)
            cursor.execute(
                f'UPDATE users SET {field_name} = ? WHERE chat_id = ?',
                (new_value, self.chat_id))
            conn.commit()
