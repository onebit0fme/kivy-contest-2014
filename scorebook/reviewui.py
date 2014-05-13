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
from kivy.lang import Builder

Builder.load_string('''
<MoveButton>:
    background_normal: 'image/b_25_r7_primary.png'
    color: (0,0,0,1)
    size_hint: (None, None)
    width: self.texture_size[0]+dp(30)
    height: dp(50)

<MoveList>:
    canvas:
        Color:
            rgb: (1,1,1)
        Rectangle:
            pos: self.pos
            size: self.size
    orientation: 'vertical'
    Label:
        text: 'Moves History'
        size_hint_y: None
        height: dp(50)
        color: (0,.5,0,1)
    ScrollView:
        GridLayout:
            id: moves
            cols: 2
            orientation: 'vertical'
            size_hint_y: None
            height: len(self.children)*dp(40)

<TheMoveButton>:
    size_hint_y: None
    height: dp(40)
    background_normal: 'image/primary.png' if root.black else 'image/clear_white.png'
    color: (1,1,1,1) if root.black else (0,0,0,1)

<GameInfo>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(200)
    padding: dp(30)
    BoxLayout:
        Label:
            text: root.white
            text_size: self.size
            valign: 'middle'
            halign: 'center'
            font_size: '20dp'
            color: (0,0,0,1)
        Label:
            text: 'vs'
            size_hint_x: .2
            color: (0,0,0,1)
        Label:
            text: root.black
            text_size: self.size
            valign: 'middle'
            halign: 'center'
            font_size: '20dp'
            color: (0,0,0,1)
    Label:
        text: 'Date: '+root.date
        text_size: self.size
        valign: 'middle'
        halign: 'left'
        color: (0,0,0,1)
    Label:
        text: 'Moves: '+root.moves
        text_size: self.size
        valign: 'middle'
        halign: 'left'
        color: (0,0,0,1)

''')

class MoveButton(Button):
    pass

class TheMoveButton(Button):
    black = BooleanProperty(False)
    move_number = NumericProperty()

class MoveList(BoxLayout):
    game = ObjectProperty()
    current_move = NumericProperty()
    def __init__(self, **kwargs):
        super(MoveList, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.game = kwargs.get('game', None)
        if self.game:
            for n, move in enumerate(self.game.move_history):
                b = False if n%2 == 0 else True
                btn = TheMoveButton(text=move, black=b, move_number=n)
                btn.bind(on_release=self.change_current)
                self.ids.moves.add_widget(btn)

    def change_current(self, obj):
        print 'pressed on move', obj
        self.current_move = obj.move_number

class GameInfo(BoxLayout):
    white = StringProperty('')
    black = StringProperty('')
    date = StringProperty('')
    moves = StringProperty('')

class GameWidget(BoxLayout):
    # game = ObjectProperty()
    board_orientation = StringProperty('horizontal')
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.game = kwargs.get('game', Game())
        self.orientation = 'vertical'
        # self.board = Popup(content=ChessboardUI(game=app.game), title='Chessboard')
        self.board = AnchorLayout(size_hint=(None, None), anchor_x='left', anchor_y='bottom', height=dp(200), width=dp(200))

        self.move_list = AnchorLayout(size_hint=(None, None), anchor_x='right', anchor_y='top', height=dp(200), width=dp(200))
        lst = MoveList(game=self.game)
        lst.bind(current_move=self.change_to_move)
        self.move_list.add_widget(lst)

        self.board.board = ChessboardUI(game=self.game)
        # self.board.add_widget(self.board.move_list)
        self.board.add_widget(self.board.board)
        # self.add_widget(self.board)

        nav = BoxLayout(size_hint_y=None, height=dp(50))
        nav.add_widget(Button(text="< Games", size_hint_x=None, width=dp(100), background_normal='image/clear_white.png', color=(0,0,0,1)))
        self.add_widget(nav)


        # info_box = BoxLayout(orientation='vertical')
        info_box = GameInfo(white="Terry", black="Garry Kasparov", date="today", moves=str(35))

        # who_label = Label(text='Garry Kasparov vs the rest of the world', font_size='18dp')
        # info_box.add_widget(who_label)
        #
        # when_label = Label(text='Date: 2014.02.02')
        # info_box.add_widget(when_label)
        #
        # moves_count = Label(text='Moves: 43')
        # info_box.add_widget(moves_count)

        moves_table=StackLayout(padding=dp(10), spacing=dp(10))
        for move in self.game.move_history:
            moves_table.add_widget(MoveButton(text=move))
        self.add_widget(info_box)
        self.add_widget(moves_table)
        # show_board = Button(size_hint_y=None, height=dp(50))
        # show_board.bind(on_press=self.board.open)
        # self.add_widget(show_board)


        orientation = 'vertical' if self.height > self.width else 'horizontal'
        self.blank = BoxLayout(size_hint_y=None, height = 0, orientation=orientation)
        self.blank.add_widget(self.board)
        self.blank.add_widget(self.move_list)
        self.add_widget(self.blank)

        self.bind(board_orientation=self.change_orient)

    def change_to_move(self, obj, value):
        print obj, value
        self.board.board.all_moves = self.game.move_history[:value+1]
        print self.game.move_history
        print self.game.move_history[:value]

    def on_touch_move(self, touch):
        self.board.height = self.board.width = touch.y
        # self.board.move_list.pos = touch.pos
        self.board.board.minimize = touch.y*1.0/self.height
        self.move_list.opacity = touch.y*1.0/self.height
        if self.board_orientation == 'horizontal':
            self.move_list.height = self.board.height
            self.move_list.width = self.width - self.height
        else:
            self.move_list.width = self.board.width
            self.move_list.height = self.height - self.width

        orientation = 'vertical' if self.height > self.width else 'horizontal'
        if self.board_orientation != orientation:
            self.board_orientation = orientation

    def change_orient(self, obj, value):
        print self.board_orientation
        self.blank.orientation = self.board_orientation
        self.blank.children[0], self.blank.children[1] = self.blank.children[1], self.blank.children[0]