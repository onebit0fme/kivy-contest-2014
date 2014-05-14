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
from datetime import datetime

from Chessnut.game import Game, InvalidMove

from scorebook.chessboard import ChessboardUI
from scorebook.reviewui import GameWidget, MoveButton
from scorebook.store import ScorebookGame
from scorebook.record import GameRecorder
# from main import app

import types
from random import choice

from kivy.lang import Builder

Builder.load_string('''
<ModeScreen>:
    BoxLayout:
        orientation: 'vertical' if self.height > self.width else 'horizontal'
        padding: (dp(20),dp(100))
        Label:
            canvas.before:
                Color:
                    rgb: (0,.5,0)
                Rectangle:
                    pos: self.pos
                    size: self.size
                Line:
                    rectangle: (self.pos[0],self.pos[1], self.size[0], self.size[1])
                    width: dp(2)
            text: 'Review games'
            font_size: '30dp'
            color: (1,1,1,1)
        Label:
            canvas:
                Color:
                    rgb: (0,.5,0)
                Line:
                    rectangle: (self.pos[0],self.pos[1], self.size[0], self.size[1])
                    width: dp(2)
            text: 'Record game'
            font_size: '30dp'
            color: (0,0,0,1)

<MenuItem>:
    canvas.before:
        Color:
            rgb: (.65,.19,0)
        Rectangle:
            pos: self.pos
            size: self.size
    text_size: self.size
    font_size: self.height/4
    valign: 'middle'
    halign: 'center'

<AppTitleLabel>:
    text: 'Chess Scorebook'
    color: (0,.5,0,1)
    font_size: '35dp'
    text_size: self.size
    valign: 'middle'
    halign: 'center'

<AppMenuInst>:
    text: 'This is main menu. Navigation is a game of chess. To make selection, put the figure (specified above) on desired cell on the board. Also, play by rules, with both, whites and blacks'
    color: (.4,.4,.4,1)
    font_size: '12dp'
    text_size: self.size
    valign: 'middle'
    halign: 'left'

<ActionFigureLabel>:
    text: root.figure_text+' makes selection'
    color: (0,0,0,1)
    font_size: '25dp'
    text_size: self.size
    valign: 'middle'
    halign: 'center'
    size_hint_y: None
    height: dp(50)

''')

class ModeScreen(Screen):
    pass

class MenuItem(Label):
    navigate_to = StringProperty('')

class AppTitleLabel(Label):
    pass

class AppMenuInst(Label):
    pass

class ActionFigureLabel(Label):
    action_chessman = StringProperty('Q')
    figure_text = StringProperty('')
    def __init__(self, **kwargs):
        super(ActionFigureLabel, self).__init__(**kwargs)
        if self.action_chessman.isupper():
            self.figure_text += "White "
        else:
            self.figure_text += "Black "
        f = self.action_chessman.lower()
        if f == 'p':
            self.figure_text += "Pawn"
        elif f == 'r':
            self.figure_text += "Rook"
        elif f == 'n':
            self.figure_text += "Knight"
        elif f == 'b':
            self.figure_text += "Bishop"
        elif f == 'q':
            self.figure_text += "Queen"
        # elif f == 'k':
        #     self.figure_text += "King"

class MenuLayoutScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuLayoutScreen, self).__init__(**kwargs)
        menu = MenuLayout()
        self.add_widget(menu)

        menu.menu.actual_board.bind(go_to=self.go_to)

    def go_to(self, obj, where):
        if where:
            if where == "Record game":
                self.parent.current = 'recorder'
            elif where == "Review games":
                self.parent.current = 'games'

class MenuLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MenuLayout, self).__init__(**kwargs)
        self.orientation = 'vertical' if self.height > self.width else 'horizontal'

        size = self.width if self.orientation == 'vertical' else self.height
        options = ['p', 'r', 'n', 'b', 'q', 'P', 'R', 'N', 'B', 'Q']
        action_chessman = choice(options)
        self.menu = ChessMenu(game=Game(), action_chessman=action_chessman, size_hint=(None, None), width=size, height=size)

        menu_title = BoxLayout(orientation="vertical", padding=dp(10))
        t = AppTitleLabel()
        f = ActionFigureLabel(action_chessman=action_chessman)
        i = AppMenuInst()
        menu_title.add_widget(t)
        menu_title.add_widget(f)
        menu_title.add_widget(i)


        self.add_widget(menu_title)
        self.add_widget(self.menu)

        self.bind(on_size=self.on_size)

    def on_size(self, obj, size):
        self.orientation = 'vertical' if self.height > self.width else 'horizontal'
        size = self.width if self.orientation == 'vertical' else self.height
        self.menu.height = size
        self.menu.width = size



class ChessMenu(ChessboardUI):
    def __init__(self, **kwargs):
        super(ChessMenu,self).__init__(**kwargs)
        self.actual_board.on_touch_up = types.MethodType( alt_on_touch_up, self.actual_board )
        # self.actual_board.go_to = StringProperty('')
        self.action_chessman = kwargs.get('action_chessman', 'Q')

        menu_items = ['Review games', 'Record game']
        places = range(24,40)
        for item in menu_items:
            print self.actual_board.children
            place = places.pop(choice(range(0,len(places))))
            self.actual_board.children[place].add_widget(MenuItem(text=item, navigate_to=item, font_size='20dp'))
            self.actual_board.action_chessman = self.action_chessman

        # for cell in self.actual_board.children[24:40]:
        #     cell.add_widget(MenuItem(text='hello', color=(0,0,0,1), navigate_to='somewhere', font_size='20dp'))

def alt_on_touch_up(self, touch):
    '''
    Replacing method for menu
    '''
    for cell in self.children:
        if cell.collide_point(*touch.pos) and self.grabbed:
            self.destination = cell.name
            try:
                self.game.apply_move(self.move_start+self.destination)
                print "Is Legal"
                if cell.children:
                    if hasattr(cell.children[0], 'navigate_to'):
                        menu_item = cell.children[0]
                        if self.grabbed.symbol == self.action_chessman:
                            print 'WE HAVE A MATCH', menu_item.navigate_to
                            self.go_to = menu_item.navigate_to

                        # move if no match
                        places = range(0,64)
                        new_place = choice(places)
                        while self.children[new_place].children or not places:
                            new_place = choice(places)
                        cell.clear_widgets()
                        self.children[new_place].add_widget(menu_item)

                        print 'got ya'

                self.grabbed.parent.clear_widgets()


                cell.clear_widgets()
                cell.add_widget(self.grabbed)
                # self.grabbed.pos = cell.pos
                self.move_made = False if self.move_made else True
            except InvalidMove:
                print 'Not Legal Move'
                self.grabbed.pos = self.grabbed.parent.pos

    if self.grabbed:
        touch.ungrab(self.grabbed)
        self.grabbed = None

class NavMenu(ScreenManager):
    def __init__(self, **kwargs):
        super(NavMenu, self).__init__(**kwargs)
        # self.add_widget(ModeScreen(name='ModeScreen'))
        screen = Screen()
        screen.add_widget(ChessMenu(game=Game()))
        self.add_widget(screen)

