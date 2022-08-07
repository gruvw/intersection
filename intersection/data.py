from __future__ import annotations
from nanoid import generate


class IntersectionData:

    def __init__(self, max_match_delay):
        self._users = {}
        # self._games = {}
        self._max_match_delay = max_match_delay
        self._waiting_room = Game(generate())

    def get_user(self, user_id):
        if user_id not in self._users:
            return None
        return self._users[user_id]

    def create_user(self, user_id, username, chat_id):
        user = User(user_id, username, chat_id)
        self._users[user_id] = user
        return user

    def get_or_create_game(self, game_name):
        if not game_name:
            # TODO Waiting room max delay
            return self._waiting_room

        for user in self._users.values():
            if user.game and user.game.name == game_name:
                return user.game

        game = Game(game_name)
        return game

    def join_game(self, user, game: Game):
        if game.is_full():
            raise Exception(f"Trying to join a game that is already full! {user}, {game}")

        user.game = game
        game._players.append(user)

        game.reset()

        if game == self._waiting_room and game.is_full():
            self._waiting_room = Game(generate())


class User:

    def __init__(self, user_id, user_name, chat_id):
        self._registered_time = 0
        self._user_id = user_id
        self.user_name = user_name
        self.chat_id = chat_id
        self.game: Game = None
        self.current_word = ""

    def was_registered_before(time):
        return True # TODO


class Game:

    def __init__(self, name):
        self.name = name
        self._players: list[User] = []
        self.words = []
        self.rounds_count = 0

    def has_already_been_used(self, word):
        for w1, w2 in self.words:
            if word == w1 or word == w2:
                return True
        return False

    def get_opponent_of(self, player):
        return self._players[0] if self._players[0] != player else self._players[1]

    def get_chat_ids(self):
        return (p.chat_id for p in self._players)

    def get_broadcast_against(self):
        return ((p.chat_id, self.get_opponent_of(p)) for p in self._players)

    def is_full(self):
        return len(self._players) >= 2

    def is_empty(self):
        return len(self._players) == 0

    def new_round(self):
        for player in self._players:
            player.current_word = ""
        self.rounds_count += 1

    def reset(self):
        for player in self._players:
            player.current_word = ""
        self.words.clear()
        self.rounds_count = 0

    def terminate(self):
        self.reset()
        for player in self._players:
            player.game = None
        self._players.clear()
