__author__ = 'onebit0fme'

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

from Chessnut.game import Game, InvalidMove

from scorebook.chessboard import ChessboardUI
from scorebook.reviewui import GameWidget, MoveButton
from scorebook.store import ScorebookGame
from datetime import datetime

class GameRecorderScreen(Screen):
    def __init__(self, **kwargs):
        super(GameRecorderScreen, self).__init__(**kwargs)
        self.recorder = GameRecorder()
        self.add_widget(self.recorder)

    def on_enter(self, *args):
        pass
        # reset the game

    def on_leave(self, *args):
        pass
        # save the game

class GameRecorder(BoxLayout):
    def __init__(self, **kwargs):
        super(GameRecorder, self).__init__(**kwargs)
        self.orientation = 'vertical' if self.height > self.width else 'horizontal'
        self.bind(size=self.on_size, orientation=self.on_orientation)

        self.game = Game()
        side_box = BoxLayout(orientation='vertical')
        save_button = Button(text='Save game', size_hint_y=None, height=dp(50))
        save_button.bind(on_release=self.save_game)
        side_box.add_widget(save_button)

        self.moves_table=StackLayout(padding=dp(10), spacing=dp(10))
        for move in self.game.move_history:
            self.moves_table.add_widget(MoveButton(text=move))

        side = self.height if self.orientation == 'horizontal' else self.width
        self.board = ChessboardUI(game=self.game, size_hint=(None,None), height=side, width=side)
        self.board.bind(move_made=self.change_moves)

        self.add_widget(self.board)
        side_box.add_widget(self.moves_table)
        self.add_widget(side_box)

    def save_game(self, obj):
        g = ScorebookGame(white="Terry", black="Someone", date=str(datetime.now()), moves=' '.join(self.game.move_history))
        g.save()

    def on_size(self, obj, size):
        self.orientation = 'vertical' if size[1] > size[0] else 'horizontal'
        side = self.height if self.orientation == 'horizontal' else self.width
        self.board.height = side
        self.board.width = side

    def on_orientation(self, obj, o):
        self.children[0], self.children[1] = self.children[1], self.children[0]

    def change_moves(self, obj, value):
        self.moves_table.clear_widgets()
        for move in self.game.move_history:
            self.moves_table.add_widget(MoveButton(text=move))
