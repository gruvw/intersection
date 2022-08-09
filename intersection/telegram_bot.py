import os
import unidecode
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler

from .data import IntersectionData


load_dotenv()
updater = Updater(token=os.getenv("INTERSECTION_TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher
bot = dispatcher.bot
bot_username = bot.name

gameData = IntersectionData(0)


# Decorators

def commandHandler(func):
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func


def messageHandler(func):
    handler = MessageHandler(Filters.text & (~Filters.command), func)
    dispatcher.add_handler(handler)
    return func


# Telegram

def broadcast(game, message, **kwargs):
    for chat_id in game.get_chat_ids():
        bot.send_message(chat_id, message, **kwargs)


def game_not_full_message(chat_id, game):
    bot.send_message(chat_id, f"📨 Two players are required to start a game. Forward the following message to your friend: ")
    bot.send_message(chat_id, f"Let's play Intersection together\!\n Join me by sending `/play {game.name}` to {bot_username}\.", parse_mode=ParseMode.MARKDOWN_V2)


@commandHandler
def start(update, context: CallbackContext):
    update.message.reply_text("👋 Hello and welcome to The Intersection Game!\nThis is a two-player game so you must find another player to start a game.\nTo do so you must use the /play command. Typing /play will put you inside a game; if another player also uses /play soon after you, the game will start with this person as the other player.\nIf you specify a password (e.g. `/play 123`) you will only play against a player who uses the same password.\nOn each round, each player must enter their word. The goal is to enter the same word based on the two previously entered ones. Words may only be used once per game.\nHave fun!\n")


@commandHandler
def help(update, context):
    update.message.reply_text("Here is the list of what you can do:\n/start - Displays the start message and the rules.\n/help - Displays a description of available commands.\n/play [password] - Starts a new game with the optional password. Places you in the waiting room if no password is provided.\n/stop - Terminates your current game.\nSimply send me your next word when within a game (won't take accents and capitals into account).")


@commandHandler
def stop(update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = gameData.get_user(user_id)
    if user:
        broadcast(user.game, "⚠️ Your old game was terminated.")
        user.game.terminate()
