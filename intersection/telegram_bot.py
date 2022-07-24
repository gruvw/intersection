import os
from dotenv import load_dotenv
from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, InlineQueryHandler

from .data import IntersectionData


load_dotenv()
updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher

gameData = IntersectionData()


def commandHandler(func):
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func


def inlineQueryHandler(func):
    dispatcher.add_handler(InlineQueryHandler(func))
    return func


@commandHandler
def start(update, context):
    update.message.reply_text('Hi!')


@commandHandler
def help(update, context):
    # TODO
    update.message.reply_text('Help!')


@commandHandler
def play(update, context):
    if not context.args:
        pass
    update.message.reply_text('coucou')


@inlineQueryHandler
def inlineQuery(update, context):
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id="1",
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id="2",
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id="3",
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]

    update.inline_query.answer(results)

