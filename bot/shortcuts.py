"""Shortcuts of the bot."""
from telegram import Bot, Message


def send_photo(url: str, bot: Bot, **kwargs) -> Message:
    """Send photo.

    Arguments:
        url - regarding the static folder.
        bot - the bot instance.
        *args - bot.send_photo arguments.
    """
    with open(f'static/{url}', 'rb') as photo:
        bot.send_photo(photo=photo, **kwargs)
