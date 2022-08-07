import os
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler

from .data import IntersectionData


load_dotenv()
updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher
bot = dispatcher.bot
bot_username = bot.name

gameData = IntersectionData(0)

default_answer_kwargs = {"cache_time": 0, "is_personal": True}


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

def broadcast(game, message):
    for chat_id in game.get_chat_ids():
        bot.send_message(chat_id, message)


def game_not_full_message(chat_id, game):
    bot.send_message(chat_id, f"Two players are required to start a game. Forward the following message to your friend: ")
    bot.send_message(chat_id, f"Let's play Intersection together\!\n Join me by sending `/play {game.name}` to {bot_username}\.", parse_mode=ParseMode.MARKDOWN_V2)


@commandHandler
def start(update, context: CallbackContext):
    update.message.reply_text("Hello and welcome to The Intersection Game!\nThis is a 2 player game so you must find another player to start a game.\nTo do so you must use the /play command. Typing /play will put you inside a game, if another player also uses /play soon after you, the game will start.\nIf you specify a password after /play you will only play against a player that used the same password.\nHave fun!")


@commandHandler
def help(update, context):
    # TODO
    update.message.reply_text('Help!')


@commandHandler
def stop(update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = gameData.get_user(user_id)
    if user:
        broadcast(user.game, "Your old game was terminated.")
        user.game.terminate()


@commandHandler
def play(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    chat_id = update.effective_chat.id

    game_name = context.args[0] if context.args else None

    user = gameData.get_user(user_id) or gameData.create_user(user_id, user_name, chat_id)

    if user.game:
        broadcast(user.game, "Your old game was terminated.")
        user.game.terminate()

    game = gameData.get_or_create_game(game_name)

    if game.is_full():
        context.bot.send_message(user.chat_id, "This game is already full!")
        return

    gameData.join_game(user, game)
    bot.send_message(user.chat_id, f"You entered the game {game.name}.")

    if game.is_full():
        for chat_id, opponent in game.get_broadcast_against():
            bot.send_message(chat_id, f"Your game is ready to start!\nYou are playing against: {opponent.user_name}.\nSend me your next word.")
        return

    game_not_full_message(user.chat_id, game)


@messageHandler
def word(update: Update, context):
    query = update.message.text.split()[0]
    user = gameData.get_user(update.message.from_user.id)
    game = user.game if user else None

    if not game:
        bot.send_message(update.effective_chat.id, f"You are not in a game...")
        return

    if not game.is_full():
        game_not_full_message(user.chat_id, game)
        return

    if user.current_word:
        bot.send_message(user.chat_id, f"You already chose your word...")
        return

    if not query:
        context.bot.send_message(user.chat_id, f"Invalid word, please try again.")
        return

    if game.has_already_been_used(query):
        context.bot.send_message(user.chat_id, f"This word has already been used, please enter another word.")
        return

    user.current_word = query

    opponent = game.get_opponent_of(user)
    if opponent.current_word:
        words = sorted([(user.user_name, user.current_word), (opponent.user_name, opponent.current_word)], key=lambda e: e[0])
        game.words.append([words[0][1], words[1][1]])
        if opponent.current_word == query:
            summary = '\n'.join(' - '.join(w) for w in game.words)
            broadcast(game, f"You won 🎉! It took you {game.rounds_count + 1} rounds to settle.\nSummary of the game:\n{summary}\nType to /play to play again.")
            game.terminate()
        else:
            for chat_id, opponent in game.get_broadcast_against():
                # TODO bold
                bot.send_message(chat_id, f"Oups, {opponent.user_name} entered **{opponent.current_word}**\. Try again\!", parse_mode=ParseMode.MARKDOWN_V2)
            game.new_round()
        return

    bot.send_message(user.chat_id, f"Your word has been registered, wait for {opponent.user_name} to enter theirs.")
    bot.send_message(opponent.chat_id, f"{user.user_name} registered their word.")


# TODO menu and botfather config
# convert word to lower and remove accents
# Emojis and text improvements
