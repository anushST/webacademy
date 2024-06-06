"""Bot's main file. Run bot here."""
import logging
from os import getenv

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)

import constants
import db_queries
from decorators import safe_handler_method
from display_data import buttons, texts
from exceptions import BadRequestError, NoTokenError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s '
                              '(def %(funcName)s:%(lineno)d)')
handler = logging.handlers.RotatingFileHandler(
        'logs/bot.log', maxBytes=5*1024*1024, backupCount=2
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_token(token: str) -> None:
    """Check if the token is None."""
    if token is None:
        logger.critical('Missing required environment variable(token)')
        raise NoTokenError('No Token')


@safe_handler_method
def start(update: Update, context: CallbackContext) -> None:
    """Send language choice.

    Calls on /start command.
    """
    keyboard = [
        [InlineKeyboardButton(
             buttons.TJ_LANG_CHOOSE_BUTTON,
             callback_data=constants.LANG_TJ_CALLBACK),
         InlineKeyboardButton(
             buttons.RU_LANG_CHOOSE_BUTTON,
             callback_data=constants.LANG_RU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.message.reply_text(texts.CHOOSE_LANG_TEXT,
                                        reply_markup=reply_markup)
    context.bot_data['lang_message_id'] = message.message_id
    update.message.delete()


@safe_handler_method
def main_menu(update: Update, context: CallbackContext) -> None:
    """Send main menu.

    Here are three navigation buttons: Contact Information, About Academy
    and Courses.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    if 'lang' in query.data:
        lang = query.data.split('_')[1]
        if lang in constants.LANGUAGES:
            lang = db_queries.save_lang(chat_id, lang)
        else:
            raise BadRequestError('Lang is in incorrect format.')
    else:
        lang = db_queries.get_lang(chat_id)

    keyboard = [
        [InlineKeyboardButton(buttons.COURSE_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)],
        [InlineKeyboardButton(buttons.ABOUT_ACADEMY_BUTTON[lang],
                              callback_data=constants.ACADEMY_DESC_CALLBACK)],
        [InlineKeyboardButton(buttons.CONTACT_INFO_BUTTON[lang],
                              callback_data=constants.CONTACT_INFO_CALLBACK),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not db_queries.get_sent_main_message(chat_id):
        with open('static/logo.jpg', 'rb') as photo:
            context.bot.send_photo(
                chat_id,
                photo,
                caption=texts.WELCOME_TEXT[lang],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        db_queries.set_sent_main_message_True(chat_id)
    else:
        query.edit_message_caption(texts.WELCOME_TEXT[lang], reply_markup)
    if 'lang_message_id' in context.bot_data:
        context.bot.delete_message(chat_id,
                                   context.bot_data['lang_message_id'])
        context.bot_data.pop('lang_message_id')


@safe_handler_method
def contact_info(update: Update, context: CallbackContext) -> None:
    """Send contact info."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    lang = db_queries.get_lang(chat_id)
    keyboard = [
        [InlineKeyboardButton(buttons.INSTAGRAM_BUTTON,
                              constants.INSTAGRAM_URL)],
        [InlineKeyboardButton(buttons.TELEGRAM_CHANNEL_BUTTON,
                              constants.TELEGRAM_CHANNEL_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.CONTACTS_TEXT[lang], reply_markup,
                               parse_mode='HTML')


@safe_handler_method
def about_academy(update: Update, context: CallbackContext) -> None:
    """Send information about academy."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    lang = db_queries.get_lang(chat_id)
    keyboard = [
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.ABOUT_ACADEMY_TEXT[lang], reply_markup,
                               parse_mode='HTML')


@safe_handler_method
def courses(update: Update, context: CallbackContext) -> None:
    """Send courses list."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    lang = db_queries.get_lang(chat_id)
    keyboard = []
    row = []
    i = 0
    for callback_data, course in texts.COURSES.items():
        callback = f'{constants.COURSE_PATTERN.split("^")[1]}{callback_data}'
        row.append(InlineKeyboardButton(course[lang]['button_text'],
                                        callback_data=callback))
        i += 1
        if i > 1:
            keyboard.append(row)
            row = []
            i = 0
    if row:
        keyboard.append(row)
    keyboard.append(
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.COURSES_LIST_TEXT[lang], reply_markup)


@safe_handler_method
def course_info(update: Update, context: CallbackContext) -> None:
    """Send information about the course."""
    query = update.callback_query
    course_name = query.data.split('_')[1]
    chat_id = update.effective_chat.id
    lang = db_queries.get_lang(chat_id)

    keyboard = [
        [InlineKeyboardButton(buttons.REGISTER_BUTTON[lang],
                              constants.REGISTER_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.COURSES[course_name][lang]['text'],
                               reply_markup=reply_markup)


def delete_user_message(update: Update, context: CallbackContext) -> None:
    """Delete all messages sent by user."""
    update.message.delete()


def main() -> None:
    """Start bot."""
    load_dotenv()
    TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
    check_token(TELEGRAM_TOKEN)
    updater = Updater(TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher
    try:
        dispatcher.add_handler(CommandHandler(constants.START_COMMAND, start))
        dispatcher.add_handler(CallbackQueryHandler(
            main_menu, pattern=constants.MAIN_MENU_PATTERN))
        dispatcher.add_handler(CallbackQueryHandler(
            contact_info, pattern=constants.CONTACT_INFO_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            about_academy, pattern=constants.ACADEMY_DESC_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            courses, pattern=constants.COURSES_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            course_info, pattern=constants.COURSE_PATTERN))
        dispatcher.add_handler(MessageHandler(Filters.all,
                                              delete_user_message))

        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f'An error occured in: {e}', exc_info=True)


if __name__ == '__main__':
    main()
