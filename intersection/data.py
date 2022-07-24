from uuid import uuid4


class IntersectionData:

    def __init__(self, max_match_delay):
        self._users = {}
        self._games = {}
        self._max_match_delay = max_match_delay
        self._waitingUser = None

    def _user_in_queue(self):
        return self._waitingUser if self._waitingUser and self._waitingUser.was_registered_before(self._max_match_delay) else None

    def _register_user(self, user_id, user_name):
        if user_id in self._users and self._users[user_id]._game:
            self._games.pop(self._users[user_id]._game._name)
            self._users[user_id]._game.terminate()
        self._users[user_id] = User(user_id, user_name)
        return self._users[user_id]

    def _register_anonymous_user(self, user):
        user_in_queue = self._user_in_queue()
        if user_in_queue:
            game = Game((user, user_in_queue), uuid4())
            self._games[game._name] = game
            return True
        self._waitingUser = user
        return False

    def _register_named_user(self, user, name):
        if name in self._games:
            return self._games[name]._add_player(user)
        game = Game((user), name)
        self._games[game._name] = game
        return True

    def register_user(self, user_id, user_name, name=None):
        user = self._register_user(user_id, user_name)
        if name:
            return self._register_named_user(user, name)
        return self._register_anonymous_user(user)


class User:

    def __init__(self, user_id, user_name):
        self._registered_time = 0
        self._user_id = user_id
        self._user_name = user_name
        self._game = None

    def _set_game(self, game):
        self._game = game

    def was_registered_before(time):
        return True # TODO


class Game:

    def __init__(self, players, name):
        self._name = name
        self._player_ids = [p._user_id for p in players]
        for p in players:
            p._set_game(self)

    def _add_player(self, player):
        if len(self._player_ids) >= 2:
            return False
        self._player_ids.append(player._user_id)
        player._set_game(self)
        return True

    def terminate(self):
        pass # TODO


# TODO add messages feedback
