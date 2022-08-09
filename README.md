# Intersection

[Telegram](https://telegram.org/) based version of a text based game where two players try to find the same word.

## Start

👋 Hello and welcome to The Intersection Game!  
This is a two-player game so you must find another player to start a game.  
To do so you must use the /play command. Typing /play will put you inside a game; if another player also uses /play soon after you, the game will start with this person as the other player.  
If you specify a password (e.g. `/play 123`) you will only play against a player who uses the same password.  
On each round, each player must enter their word. The goal is to enter the same word based on the two previously entered ones. Words may only be used once per game.  
Have fun!

## Help

Here is the list of what you can do:  
/start - Displays the start message and the rules.  
/help - Displays a description of available commands.  
/play [password] - Starts a new game with the optional password. Places you in the waiting room if no password is provided.  
/stop - Terminates your current game.  
Simply send me your next word when within a game (won't take accents and capitals into account).

## Run instance

1. Install using `pip install intersection`
2. Specify the environnement variable `INTERSECTION_TELEGRAM_BOT_TOKEN`
3. Start the bot using the `intersection-game` command
