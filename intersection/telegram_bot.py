import os
from dotenv import load_dotenv
from telegram import ParseMode, InputTextMessageContent, Update, InlineQueryResultArticle, InputMessageContent
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackContext, ChosenInlineResultHandler

from .data import IntersectionData, User


load_dotenv()
updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher
bot_username = dispatcher.bot.name

gameData = IntersectionData(0)


# Decorators

def commandHandler(func):
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func


def inlineQueryHandler(func):
    dispatcher.add_handler(InlineQueryHandler(func))
    return func


def chosenInlineResultHandler(func):
    dispatcher.add_handler(ChosenInlineResultHandler(func))
    return func


# Telegram

@commandHandler
def start(update, context: CallbackContext):
    update.message.reply_text("Hello and welcome to The Intersection Game!\nThis is a 2 player game so you must find another player to start a game.\nTo do so you must use the /play command. Typing /play will put you inside a game, if another player also uses /play soon after you, the game will start.\nIf you specify a password after /play you will only play against a player that used the same password.\nHave Fun !")


@commandHandler
def help(update, context):
    # TODO
    update.message.reply_text('Help!')


@commandHandler
def play(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    chat_id = update.effective_chat.id

    game_name = context.args[0] if context.args else None

    user = gameData.get_user(user_id) or gameData.create_user(user_id, user_name, chat_id)

    if user.game:
        for chat_id in user.game.get_chat_ids():
            context.bot.send_message(chat_id, "Your game was terminated.")
        user.game.terminate()

    game = gameData.get_or_create_game(game_name)

    if game.is_full():
        context.bot.send_message(user.chat_id, "This game is already full!")
        return

    gameData.join_game(user, game)
    context.bot.send_message(user.chat_id, f"You entered the game {game.name}.")

    if game.is_full():
        for chat_id, opponents in game.get_broadcast_against():
            context.bot.send_message(chat_id, f"Your game is ready to start!\nYou are playing against: {','.join(o.user_name for o in opponents)}.")
        return

    context.bot.send_message(user.chat_id, f"Waiting for another player to join the game...")


@inlineQueryHandler
def inlineQuery(update: Update, context):
    query = update.inline_query.query

    user = gameData.get_user(update.inline_query.from_user.id)
    game = user.game if user else None

    if not game:
        update.inline_query.answer([], switch_pm_text="Play !", switch_pm_parameter="_")
        return

    if not game.is_full():
        results = [
            InlineQueryResultArticle(
                id="0",
                title="Invite player",
                description="Two players are required to start the game.",
                input_message_content=InputTextMessageContent(f"Play Intersection with me using {bot_username}."),
            )
        ]
        update.inline_query.answer(results)
        return

    if query == "":
        return

    other_player = game.get_players_except(user)[0]
    if other_player.current_word:
        result_message = f"You won 🎉! It took you {game.rounds_count} rounds to settle.\nTalk to {bot_username} to play again." if other_player.current_word == query else "Try again!"
        results = [
            InlineQueryResultArticle(
                id="2",
                title="Submit Your Word",
                input_message_content=InputTextMessageContent(f"Summary:\n1. {other_player.user_name} -> {other_player.current_word}\n2. {user.user_name} -> {query}\n\n{result_message}"),
            )
        ]
        update.inline_query.answer(results)
        return

    # TODO id 1
    update.inline_query.answer(results)


@chosenInlineResultHandler
def inlineResult(update: Update, context: CallbackContext):
    pass
