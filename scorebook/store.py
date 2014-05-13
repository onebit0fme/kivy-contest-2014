__author__ = 'onebit0fme'
from kivy.storage.jsonstore import JsonStore

def get_games():
    # todo: make decorator filtering
    store = JsonStore('games.json')
    games = []
    for key in store:
        data = store[key]
        g = ScorebookGame(white=data['white'], black=data['black'], date=data['date'], moves=data['moves'], id=data['id'])
        games.append(g)
    return games


class ScorebookGame(object):
    def __init__(self, white='', black='', date='', moves='', id=None):
        # things that is stored
        self.id = id
        self.white = white
        self.black = black
        self.date = date
        self.moves = moves # string

        # the rest
        self.moves_list = ScorebookGame.convert_moves(moves)

    @property
    def move_count(self):
        return len(self.moves_list)

    @property
    def json_dict(self):
        all = self.__dict__
        to_store = ['white', 'black', 'date', 'moves', 'id']
        jd = {}
        for what in to_store:
            jd[what] = all[what]
        return jd

    @staticmethod
    def convert_moves(moves_string):
        return moves_string.split(' ')

    @staticmethod
    def get_unique_id():
        store = JsonStore('games.json')
        ids = []
        for key in store:
            ids.append(int(key))
        if ids:
            return max(ids)+1
        else:
            return 1

    def save(self):
        # TODO: Would be a good idea to store in .pgn format. Hmm, maybe later. Plus, it requires Algebraic Notation converter.
        if not self.id:
            self.id = ScorebookGame.get_unique_id()
        store = JsonStore('games.json')
        store[str(self.id)] = self.json_dict

# g = ScorebookGame('the rest of the world', 'Garry Kasparow', 'today', 'e2e4 r4t4 j6j3 k2k5 l6l5', 1)
# g.save()
# print get_games()
# print ScorebookGame.get_unique_id()