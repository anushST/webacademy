"""Bot's decorators."""
import logging
import logging.handlers

from telegram.error import BadRequest

from display_data import texts

logger = logging.getLogger('__main__')


def safe_handler_method(func):
    """Safely execute handlers and log exceptions."""
    def wrapper(update, context):
        try:
            return func(update, context)
        except BadRequest as e:
            if not str(e) == ('Message is not modified: specified new message '
                              'content and reply markup are exactly the same '
                              'as a current content and reply markup of the '
                              'message'):
                logger.error(f'Bad request in {func.__name__}: {e}',
                             exc_info=True)
        except Exception as e:
            logger.error(f'Error in handler {func.__name__}: {e}',
                         exc_info=True)
            context.bot.send_message(
                update.effective_chat.id,
                texts.ERROR_TEXT,
                parse_mode='HTML'
            )
    return wrapper
