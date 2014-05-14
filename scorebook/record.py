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
from scorebook.reviewui import GameWidget, MoveButton, MoveLabel
from scorebook.store import ScorebookGame

from kivy.lang import Builder

Builder.load_string('''
<CustomButton>:
    font_size: '18dp'
    color: (0,.5,0,1)
    background_normal: 'image/clear_white.png'
    background_down: 'image/primary.png'

<CustomLabel>:
    font_size: '18dp'
    color: (0,0,0,1)

<CustomPopup>:
    background_color: (1,1,1,.5)
    size_hint: (.7,.6)
    pos_hint: {'top': 1}
    background: 'image/wash_white.png'
    title_color: (0,.5,0,1)
    separator_color: (0,.5,0,1)


<MovesGrid>:
    cols: 2
    orientation: 'vertical'
    size_hint_y: None
    height: (len(self.children)+1)*dp(50)
    # on_children: self.height = (len(self.children)+1)*dp(50)
''')

class CustomButton(Button):
    pass

class CustomLabel(Label):
    pass

class CustomPopup(Popup):
    pass

class MovesGrid(GridLayout):
    pass

class SaveFormPopup(CustomPopup):
    save = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(SaveFormPopup, self).__init__(**kwargs)
        self.white = TextInput(text='', multiline=False)
        self.black = TextInput(text='', multiline=False)
        self.event = TextInput(text='', multiline=False)
        self.round = TextInput(text='', multiline=False)
        save = CustomButton(text='Save')
        save.bind(on_release=self.save_it)

        form_box = BoxLayout(orientation='vertical')
        form_box.add_widget(CustomLabel(text='White Player'))
        form_box.add_widget(self.white)
        form_box.add_widget(CustomLabel(text='Black Player'))
        form_box.add_widget(self.black)
        form_box.add_widget(CustomLabel(text='Event'))
        form_box.add_widget(self.event)
        form_box.add_widget(CustomLabel(text='Round'))
        form_box.add_widget(self.round)

        # custom date
        form_box.add_widget(CustomLabel(text='Custom day (current if empty)'))
        l = BoxLayout()
        l.add_widget(CustomLabel(text='Year'))
        l.add_widget(CustomLabel(text='Month'))
        l.add_widget(CustomLabel(text='Day'))
        form_box.add_widget(l)

        box = BoxLayout()
        self.year = TextInput(text='', multiline=False)
        self.month = TextInput(text='', multiline=False)
        self.day = TextInput(text='', multiline=False)
        box.add_widget(self.year)
        box.add_widget(self.month)
        box.add_widget(self.day)
        form_box.add_widget(box)

        form_box.add_widget(save)

        self.content = form_box

    def save_it(self, obj):
        # king of my trick to trigger callback, value does not matter, matters only change
        self.save = False if self.save else True


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
        back_button = CustomButton(text='<< Games <<', size_hint_y=None, height=dp(50))
        back_button.bind(on_release=self.go_back)

        save_button = CustomButton(text='Save game', size_hint_y=None, height=dp(50))
        save_button.bind(on_release=self.save_popup)
        side_box.add_widget(back_button)
        side_box.add_widget(save_button)


        moves_scroll = ScrollView()
        self.moves_table=MovesGrid(padding=dp(10), spacing=dp(10))
        for move in self.game.move_history:
            self.moves_table.add_widget(MoveButton(text=move))

        side = self.height if self.orientation == 'horizontal' else self.width
        self.board = ChessboardUI(game=self.game, size_hint=(None,None), height=side, width=side)
        self.board.bind(move_made=self.change_moves)

        self.add_widget(self.board)
        moves_scroll.add_widget(self.moves_table)
        side_box.add_widget(moves_scroll)
        self.add_widget(side_box)

    def go_back(self, obj):
        content = BoxLayout()
        yes = CustomButton(text="Yes")
        yes.bind(on_release=self.save_popup)
        no = CustomButton(text="No")
        no.bind(on_release=self.back)
        content.add_widget(no)
        content.add_widget(yes)
        p = CustomPopup(title="Save game?", content=content)
        self.parent.bind(on_leave=p.dismiss)
        p.open()

    def save_popup(self, obj):
        p = SaveFormPopup(title="Save game")
        p.bind(save=self.save_game)
        p.open()

    def back(self, obj):
        self.parent.parent.current = 'games'

    def save_game(self, obj, value=None):
        if obj.year and obj.month and obj.day:
            try:
                datetime.date(obj.year, obj.month, obj.day)
                date = "{0}-{1}-{2} 00:00:00".format(obj.year, obj.month, obj.day)
            except ValueError:
                date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        g = ScorebookGame(white=obj.white.text, black=obj.black.text, event=obj.event.text, date=date, round=obj.round, moves=' '.join(self.game.move_history))
        g.save()
        obj.dismiss()
        self.parent.parent.current = 'games'

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
            self.moves_table.add_widget(MoveLabel(text=move))
