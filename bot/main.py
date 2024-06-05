"""Bot's main file. Run bot here."""
import logging
from os import getenv

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Updater,)

import constants
from display_data import buttons, texts
from exceptions import NoTokenError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s '
                              '(def %(funcName)s:%(lineno)d)')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_token(token):
    """Check if the token is None."""
    if token is None:
        logger.critical('Missing required environment variable(token)')
        raise NoTokenError('No Token')


def start(update: Update, context: CallbackContext) -> None:
    """Send language choice.

    Calls on /start command.
    """
    context.user_data.clear()
    context.bot_data.clear()
    context.bot_data['sent_main_message'] = False
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


def main_menu(update: Update, context: CallbackContext) -> None:
    """Send main menu.

    Here is three navigation buttons: Contact Information, About Academy
    and Courses.
    """
    query = update.callback_query
    if 'lang' not in context.user_data:
        lang = query.data.split('_')[1]
        context.user_data['lang'] = lang
    else:
        lang = context.user_data.get('lang', constants.RU)

    keyboard = [
        [InlineKeyboardButton(buttons.COURSE_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)],
        [InlineKeyboardButton(buttons.ABOUT_ACADEMY_BUTTON[lang],
                              callback_data=constants.ACADEMY_DESC_CALLBACK)],
        [InlineKeyboardButton(buttons.CONTACT_INFO_BUTTON[lang],
                              callback_data=constants.CONTACT_INFO_CALLBACK),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = update.effective_chat.id
    if not context.bot_data['sent_main_message']:
        with open('static/logo.jpg', 'rb') as photo:
            context.bot.send_photo(
                chat_id,
                photo,
                caption=texts.WELCOME_TEXT[lang],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        context.bot_data['sent_main_message'] = True
    else:
        query.edit_message_caption(texts.WELCOME_TEXT[lang], reply_markup)
    if 'lang_message_id' in context.bot_data:
        context.bot.delete_message(chat_id,
                                   context.bot_data['lang_message_id'])
        context.bot_data.pop('lang_message_id')


def contact_info(update: Update, context: CallbackContext) -> None:
    """Send contact info."""
    query = update.callback_query
    lang = context.user_data.get('lang', constants.RU)
    keyboard = [
        [InlineKeyboardButton(buttons.INSTAGRAM_BUTTON,
                              constants.INSTAGRAM_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.CONTACTS_TEXT[lang], reply_markup)


def about_academy(update: Update, context: CallbackContext) -> None:
    """Send information about academy."""
    query = update.callback_query
    lang = context.user_data.get('lang', constants.RU)
    keyboard = [
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.ABOUT_ACADEMY_TEXT[lang], reply_markup)


def courses(update: Update, context: CallbackContext) -> None:
    """Send courses list."""
    query = update.callback_query
    lang = context.user_data.get('lang', constants.RU)
    keyboard = [[InlineKeyboardButton(course)] for course in texts.COURSES]
    keyboard = []
    for callback_data, course in texts.COURSES.items():
        callback = f'{constants.COURSE_PATTERN.split("^")[1]}{callback_data}'
        keyboard.append([InlineKeyboardButton(course[lang]['button_text'],
                                              callback_data=callback)])
    keyboard.append(
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.COURSES_LIST_TEXT[lang], reply_markup)


def course_info(update: Update, context: CallbackContext) -> None:
    """Send information about the course."""
    query = update.callback_query
    course_name = query.data.split('_')[1]
    lang = context.user_data['lang']

    keyboard = [
        [InlineKeyboardButton(buttons.REGISTER_BUTTON[lang],
                              constants.REGISTER_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_caption(texts.COURSES[course_name][lang]['text'],
                               reply_markup=reply_markup)


def main() -> None:
    """Start bot."""
    load_dotenv()
    TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
    check_token(TELEGRAM_TOKEN)
    updater = Updater(TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

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

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
