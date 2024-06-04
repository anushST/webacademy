"""Bot's main file. Run bot here."""
import logging
from os import getenv

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Updater,)

from . import constants
from display_data import buttons, texts

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s '
                              '(def %(funcName)s:%(lineno)d)')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


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
    update.message.reply_text(texts.CHOOSE_LANG_TEXT,
                              reply_markup=reply_markup)
    update.message.delete()


def main_menu(update: Update, context: CallbackContext) -> None:
    """Send main menu.

    Here is three navigation buttons: Contact Information, About Academy
    and Courses.
    """
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang

    keyboard = [
        [InlineKeyboardButton(buttons.CONTACT_INFO_BUTTON[lang],
                              callback_data=constants.CONTACT_INFO_CALLBACK),
         InlineKeyboardButton(buttons.ABOUT_ACADEMY_BUTTON[lang],
                              callback_data=constants.ACADEMY_DESC_CALLBACK)],
        [InlineKeyboardButton(buttons.COURSE_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if lang == 'en':
        text = 'Main Menu'
    else:
        text = 'Главное меню'

    query.edit_message_text(text=text, reply_markup=reply_markup)


def contact_info(update: Update, context: CallbackContext) -> None:
    """Send contact info."""
    query = update.callback_query
    lang = context.user_data.get('lang', constants.RU)
    keyboard = [
        [InlineKeyboardButton(buttons.INSTAGRAM_BUTTON,
                              url=constants.INSTAGRAM_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON,
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=texts.CONTACTS_TEXT[lang],
                            reply_markup=reply_markup)


def about_academy(update: Update, context: CallbackContext) -> None:
    """Send information about academy."""
    query = update.callback_query
    lang = context.user_data.get('lang', constants.RU)
    keyboard = [
        [InlineKeyboardButton(buttons.BACK_BUTTON,
                              callback_data=constants.MAIN_MENU_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=texts.ABOUT_ACADEMY_TEXT[lang],
                            reply_markup=reply_markup)


def courses(update: Update, context: CallbackContext) -> None:
    """Send courses list."""
    pass
# Обработчик выбора курса
def course_info(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    course_code = query.data.split('_')[1]
    course = courses[course_code]
    lang = context.user_data['lang']

    text = (f"{course['name'][lang]}\n"
            f"Price: {course['price']}\n"
            f"Duration: {course['duration']}\n"
            f"Level: {course['level'][lang]}")

    keyboard = [
        [InlineKeyboardButton('Back to Courses', callback_data='courses')],
        [InlineKeyboardButton('Back to Menu', callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


def back_to_menu(update: Update, context: CallbackContext) -> None:
    lang = context.user_data['lang']

    keyboard = [
        [InlineKeyboardButton('Contact Information', callback_data='contact_info'),
         InlineKeyboardButton('About Academy', callback_data='academy_desc')],
        [InlineKeyboardButton('Courses', callback_data='courses')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if lang == 'en':
        text = 'Main Menu'
    else:
        text = 'Главное меню'

    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


def main() -> None:
    """Start bot."""
    load_dotenv()
    TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
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
        course_info, pattern=constants.COURSE_PATTERN))
    dispatcher.add_handler(CallbackQueryHandler(
        back_to_menu, pattern='^back_to_menu$'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
