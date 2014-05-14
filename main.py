__author__ = 'onebit0fme'
__foreword__ = "Started in the last week of the contest, so please don't judge to harsh the coding. All the best! =)"

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle, Line, Ellipse, Rotate
from kivy.uix.label import Label
from kivy.uix.scatterlayout import Scatter
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget, EventLoop
from kivy.uix.button import Button
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from functools import partial
from kivy.event import EventDispatcher
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, FadeTransition, SwapTransition, WipeTransition, FallOutTransition, RiseInTransition, NoTransition
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.carousel import Carousel
from kivy.uix.settings import SettingsWithSidebar, SettingsWithSpinner, SettingsWithTabbedPanel, SettingsWithNoMenu, Settings, SettingsPanel
import datetime
from kivy.config import ConfigParser
import webbrowser
from pprint import pprint
import re
from datetime import datetime

from Chessnut.game import Game, InvalidMove

from scorebook.chessboard import ChessboardUI
from scorebook.reviewui import GameWidgetScreen, GameWidget
from scorebook.store import ScorebookGame, get_games
from scorebook.record import GameRecorderScreen
from scorebook.menu import MenuLayoutScreen

import types
from random import choice

class GamesListScreen(Screen):
    def __init__(self, **kwargs):
        super(GamesListScreen, self).__init__(**kwargs)
        self.games = GamesList()
        self.add_widget(self.games)

    def on_enter(self, *args):
        self.games.read_games()


class GamesList(BoxLayout):
    def __init__(self, **kwargs):
        super(GamesList, self).__init__(**kwargs)
        self.games = get_games()
        for game in self.games:
            name = '{} vs {} ({})'.format(game.white, game.black, game.date)
            self.ids.games.add_widget(GameButton(text=name))

    def go_to(self, where):
        self.parent.parent.current = where

    def open_game(self, obj):
        for game in self.games:
            if game.id == obj.game_id:
                self.parent.parent.switch_to(GameWidgetScreen(game=game))

    def read_games(self):
        self.ids.games.clear_widgets()
        self.games = get_games()
        for game in self.games:
            name = '{} vs {} ({})'.format(game.white, game.black, datetime.strptime(game.date, "%Y-%m-%d %H:%M:%S").strftime('%Y.%m.%d'))
            b = GameButton(text=name, game_id=game.id)
            b.bind(on_release=self.open_game)
            self.ids.games.add_widget(b)


class GameButton(Button):
    game_id = NumericProperty()

class ScorebookApp(App):

    def build(self):

        self.sm = ScreenManager(transition=FadeTransition())
        # MENU SCREEN
        menu_screen = MenuLayoutScreen(name='menu')
        self.sm.add_widget(menu_screen)

        # GAME RECORDER SCREEN
        recorder = GameRecorderScreen(name='recorder')
        self.sm.add_widget(recorder)

        # GAME LIST
        games = GamesListScreen(name='games')
        self.sm.add_widget(games)

        self.sm.current = 'recorder'
        return self.sm

    def on_pause(self):
        return True

    def on_resume(self):
        pass


    def get_color(self, color, opacity=None):
        if opacity:
            return self.colors[color]
        else:
            return self.colors[color]+(opacity,)

Window.clearcolor = (1,1,1,1)
app = ScorebookApp()
if __name__ == '__main__':
    app.run()