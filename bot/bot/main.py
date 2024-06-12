"""Bot's main file."""
import logging
from os import getenv

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)

from . import constants
from . import db_queries
from .decorators import safe_handler_method
from .exceptions import BadRequestError, LangNotChosenError, NoTokenError
from display_data import buttons, texts
from utils.paginators import Paginator
from utils.shortcuts import send_photo

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
    db_queries.create_user(update.effective_chat.id)
    keyboard = [
        [InlineKeyboardButton(
             buttons.TJ_LANG_CHOOSE_BUTTON,
             callback_data=f'{constants.LANG_PATTERN}{constants.TJ}'),
         InlineKeyboardButton(
             buttons.RU_LANG_CHOOSE_BUTTON,
             callback_data=f'{constants.LANG_PATTERN}{constants.RU}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.message.reply_text(texts.CHOOSE_LANG_TEXT,
                                        reply_markup=reply_markup)
    context.bot_data['lang_message_id'] = message.message_id
    update.message.delete()


@safe_handler_method
def save_lang(update: Update, context: CallbackContext) -> None:
    """Save users language and call main_menu."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    lang = query.data.split(constants.LANG_PATTERN)[1]
    if lang in constants.LANGUAGES:
        db_queries.User(chat_id).edit_field('lang', lang)
    else:
        raise BadRequestError('Lang is in incorrect format.')
    main_menu(update, context)


@safe_handler_method
def main_menu(update: Update, context: CallbackContext) -> None:
    """Send main menu.

    Here are three navigation buttons: Contact Information, About Academy
    and Courses.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    lang = db_queries.User(chat_id).get_field('lang')
    if lang is None:
        raise LangNotChosenError

    keyboard = [
        [InlineKeyboardButton(buttons.COURSE_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)],
        [InlineKeyboardButton(buttons.ABOUT_ACADEMY_BUTTON[lang],
                              callback_data=constants.ACADEMY_DESC_CALLBACK)],
        [InlineKeyboardButton(buttons.CONTACT_INFO_BUTTON[lang],
                              callback_data=constants.CONTACT_INFO_CALLBACK),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user_object = db_queries.User(chat_id)
    if not user_object.get_field('main_message_id'):
        message = send_photo(
            url='logo.jpg',
            bot=context.bot,
            chat_id=chat_id,
            caption=texts.WELCOME_TEXT[lang],
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        user_object.edit_field('main_message_id', message.message_id)
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
    lang = db_queries.User(chat_id).get_field('lang')
    if lang is None:
        raise LangNotChosenError
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
    lang = db_queries.User(chat_id).get_field('lang')
    if lang is None:
        raise LangNotChosenError
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
    lang = db_queries.User(chat_id).get_field('lang')
    if lang is None:
        raise LangNotChosenError
    page = int(query.data.split(constants.COURSES_PATTERN)[1])
    paginator = Paginator(texts.COURSES,
                          constants.COURSES_PATTERN,
                          constants.ITEMS_PER_PAGE)
    keyboard = []

    for callback_data, course in paginator.get_page(page):
        callback = f'{constants.COURSE_PATTERN}{callback_data}'
        button_text = course[lang]['button_text'][:16]
        keyboard.append([InlineKeyboardButton(button_text,
                                              callback_data=callback)])

    keyboard.append(paginator.create_pagination_buttons(page))
    keyboard.append(
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.MAIN_MENU_CALLBACK)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    main_message_id = db_queries.User(
        chat_id).get_field('main_message_id')
    caption = texts.COURSES_LIST_TEXT[lang]
    if not main_message_id:
        message = send_photo(
            url='logo.jpg',
            bot=context.bot,
            chat_id=chat_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        db_queries.User(chat_id).edit_field('main_message_id',
                                            message.message_id)
    else:
        query.edit_message_caption(caption, reply_markup)

    course_info_message_id = db_queries.User(
        chat_id).get_field('course_info_message_id')
    if course_info_message_id:
        query.delete_message(course_info_message_id)
        db_queries.User(chat_id).edit_field('course_info_message_id',
                                            None)


@safe_handler_method
def course_info(update: Update, context: CallbackContext) -> None:
    """Send information about the course."""
    query = update.callback_query
    course_name = query.data.split('_')[1]
    chat_id = update.effective_chat.id
    lang = db_queries.User(chat_id).get_field('lang')
    if lang is None:
        raise LangNotChosenError
    keyboard = [
        [InlineKeyboardButton(buttons.REGISTER_BUTTON[lang],
                              constants.REGISTER_URL)],
        [InlineKeyboardButton(buttons.BACK_BUTTON[lang],
                              callback_data=constants.COURSES_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    course_info_message_id = db_queries.User(
        chat_id).get_field('course_info_message_id')
    caption = texts.COURSES[course_name][lang]['text']
    if not course_info_message_id:
        message = send_photo(
            url=texts.COURSES[course_name]['photo_url'],
            bot=context.bot,
            chat_id=chat_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        db_queries.User(chat_id).edit_field('course_info_message_id',
                                            message.message_id)
    main_message_id = db_queries.User(
        chat_id).get_field('main_message_id')
    if main_message_id:
        query.delete_message(main_message_id)
        db_queries.User(chat_id).edit_field('main_message_id', None)


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
            save_lang, pattern=constants.LANG_PATTERN))
        dispatcher.add_handler(CallbackQueryHandler(
            main_menu, pattern=constants.MAIN_MENU_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            contact_info, pattern=constants.CONTACT_INFO_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            about_academy, pattern=constants.ACADEMY_DESC_CALLBACK))
        dispatcher.add_handler(CallbackQueryHandler(
            courses, pattern=f'^{constants.COURSES_PATTERN}'))
        dispatcher.add_handler(CallbackQueryHandler(
            course_info, pattern=f'^{constants.COURSE_PATTERN}'))
        dispatcher.add_handler(MessageHandler(Filters.all,
                                              delete_user_message))

        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f'An error occured in: {e}', exc_info=True)
