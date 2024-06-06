"""Database queries."""
import sqlite3

from exceptions import NoLangChosenError


def get_lang(chat_id: int) -> str:
    """Get lang from database if exists.

    Raises NoLangChosenError if lang doesn't exist.
    """
    with sqlite3.connect('bot/db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT lang FROM users WHERE chat_id = ?
        ''', (chat_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise NoLangChosenError


def save_lang(chat_id: int, lang: str) -> str:
    """Save lang to database if doesn't."""
    with sqlite3.connect('bot/db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (chat_id, lang, sent_main_message)
            VALUES (?, ?, ?)
            ''', (chat_id, lang, False))
        cursor.execute('''
        SELECT lang FROM users WHERE chat_id = ?
        ''', (chat_id,))
        return cursor.fetchone()[0]


def set_sent_main_message_True(chat_id: int) -> None:
    """Set sent_main_message field in database True."""
    with sqlite3.connect('bot/db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET sent_main_message = ? WHERE chat_id = ?',
            (True, chat_id))


def get_sent_main_message(chat_id: int) -> bool:
    """Get sent_main_message field from database."""
    with sqlite3.connect('bot/db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT sent_main_message FROM users WHERE chat_id = ?
        ''', (chat_id,))
        return cursor.fetchone()[0]
