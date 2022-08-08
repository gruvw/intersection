from .telegram_bot import *

@commandHandler
def play(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    chat_id = update.effective_chat.id

    game_name = unidecode.unidecode(context.args[0]).lower() if context.args else None

    user = gameData.get_user(user_id) or gameData.create_user(user_id, user_name, chat_id)

    if user.game:
        stop(update, context)

    game = gameData.get_or_create_game(game_name)

    if game.is_full():
        context.bot.send_message(user.chat_id, "⚠️ This game is already full!")
        return

    gameData.join_game(user, game)
    bot.send_message(user.chat_id, f"🚪 You entered the game {game.name}.")

    if game.is_full():
        for chat_id, opponent in game.get_broadcast_against():
            bot.send_message(chat_id, f"✅ Your game is ready to start\!\nYou are playing against: *{opponent.user_name}*\.\nSend me your next word\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    game_not_full_message(user.chat_id, game)


@messageHandler
def word(update: Update, context):
    query = unidecode.unidecode(update.message.text.split()[0]).lower()
    user = gameData.get_user(update.message.from_user.id)
    game = user.game if user else None

    if not game:
        bot.send_message(update.effective_chat.id, f"⚠️ You are not in a game...")
        return

    if not game.is_full():
        game_not_full_message(user.chat_id, game)
        return

    if user.current_word:
        bot.send_message(user.chat_id, f"⚠️ You already chose your word...")
        return

    if not query:
        context.bot.send_message(user.chat_id, f"⚠️ Invalid word, please try again.")
        return

    if game.has_already_been_used(query):
        context.bot.send_message(user.chat_id, f"⚠️ This word has already been used, please enter another word.")
        return

    user.current_word = query

    opponent = game.get_opponent_of(user)
    if opponent.current_word:
        words = sorted([(user.user_name, user.current_word), (opponent.user_name, opponent.current_word)], key=lambda e: e[0])
        game.words.append([words[0][1], words[1][1]])
        if opponent.current_word == query:
            players = f"{words[0][0]} \& {words[1][0]}\n"
            summary = '\n'.join(' \- '.join(w) for w in game.words)
            broadcast(game, f"🎉 You won! Summary of the game:")
            broadcast(game, f"It took *{game.rounds_count + 1} round{'s' if game.rounds_count else ''}* for {players} to settle\.\n{summary}\nSend /play to {bot_username} to play Intersection\.", parse_mode=ParseMode.MARKDOWN_V2)
            game.terminate()
        else:
            for chat_id, opponent in game.get_broadcast_against():
                bot.send_message(chat_id, f"✏ Oups, {opponent.user_name} entered *__{opponent.current_word}__*\. Try again\!", parse_mode=ParseMode.MARKDOWN_V2)
            game.new_round()
        return

    bot.send_message(user.chat_id, f"Your word has been registered, wait for {opponent.user_name} to enter theirs.")
    bot.send_message(opponent.chat_id, f"{user.user_name} registered their word.")
