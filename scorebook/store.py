__author__ = 'onebit0fme'
from kivy.storage.jsonstore import JsonStore
from Chessnut.game import Game

def get_games():
    # todo: make decorator filtering
    store = JsonStore('games.json')
    games = []
    for key in store:
        data = store[key]
        g = ScorebookGame(white=data['white'], black=data['black'], date=data['date'], moves=data['moves'], id=data['id'], event=data['event'])
        games.append(g)
    return games


class ScorebookGame(object):
    def __init__(self, white='', black='', event='', date='', moves='', round=1, id=None):
        # things that is stored
        self.id = int(id) if id else None
        self.white = white
        self.black = black
        self.event = event
        self.date = date
        self.round = round
        self.moves = moves # string

        # the rest
        self.moves_list = ScorebookGame.convert_moves(moves)
        self.game = Game()

        self.update()

    @property
    def move_count(self):
        return len(self.moves_list)

    @property
    def json_dict(self):
        all = self.__dict__
        to_store = ['white', 'black', 'event', 'date', 'moves', 'round', 'id']
        jd = {}
        for what in to_store:
            jd[what] = all[what]
        return jd

    @staticmethod
    def convert_moves(moves_string):
        return moves_string.split(' ') if moves_string else []

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

    def update(self):
        print self.moves_list
        for move in self.moves_list:
            if move:
                self.game.apply_move(move)

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