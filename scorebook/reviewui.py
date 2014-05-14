__author__ = 'onebit0fme'
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
import datetime
from scorebook.chessboard import ChessboardUI
from scorebook.store import ScorebookGame
from kivy.lang import Builder
from math import ceil

Builder.load_string('''
<NavButton>:
    background_normal: 'image/clear_white.png'
    color: (0,.5,0,1)

<MoveButton>:
    background_normal: 'image/b_25_r7_primary.png'
    color: (0,0,0,1)
    size_hint: (None, None)
    width: self.texture_size[0]+dp(30)
    height: dp(50)

<MoveLabel>:
    canvas.before:
        Color:
            rgb: (0,.5,0)
        Rectangle:
            pos: self.pos
            size: self.size
    color: (1,1,1,1)
    size_hint: (None, None)
    width: self.texture_size[0]+dp(30)
    height: dp(20)

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
            height: (len(self.children)+1)*dp(20)
    BoxLayout:
        size_hint_y: None
        height: dp(50)
        NavButton:
            text: 'Previous'
            on_release: root.prev()
        NavButton:
            text: 'Stop' if root.in_play else 'Play'
            on_release: root.play(self)
        NavButton:
            text: 'Next'
            on_release: root.next()

<TheMoveButton>:
    canvas.before:
        Color:
            rgb: (0,.5,0) if root.black else (1,1,1)
        Rectangle:
            pos: self.pos
            size: self.size
    size_hint_y: None
    height: dp(40)
    background_normal: 'image/clear_white.png'
    color: (1,1,1,1) if root.black else (0,0,0,1)

<GameInfo>:
    orientation: 'vertical'
    # size_hint_y: None
    # height: dp(200)
    padding: dp(30)
    BoxLayout:
        Image:
            source: 'image/K_100.png'
            size_hint_x: None
            width: dp(50)
        Label:
            text: root.white
            text_size: self.size
            valign: 'middle'
            halign: 'center'
            font_size: '16dp'
            color: (0,.5,0,1)
        Label:
            text: 'vs'
            size_hint_x: .2
            color: (0,.5,0,1)
        Image:
            source: 'image/k_100.png'
            size_hint_x: None
            width: dp(50)
        Label:
            text: root.black
            text_size: self.size
            valign: 'middle'
            halign: 'center'
            font_size: '16dp'
            color: (0,.5,0,1)
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
    Label:
        text: 'Event: '+root.event
        text_size: self.size
        valign: 'middle'
        halign: 'left'
        color: (0,0,0,1)
    Label:
        text: 'FEN: '+root.fen
        text_size: self.size
        valign: 'middle'
        halign: 'left'
        color: (0,0,0,1)

''')

class MoveLabel(Label):
    pass

class MoveButton(Button):
    pass

class NavButton(Button):
    pass

class TheMoveButton(Button):
    black = BooleanProperty(False)
    move_number = NumericProperty()

class MoveList(BoxLayout):
    game = ObjectProperty()
    current_move = NumericProperty()
    in_play = BooleanProperty(False)
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
            # self.current_move = len(self.game.move_history)-1

    def change_current(self, obj):
        # print 'pressed on move', obj
        self.current_move = obj.move_number

    def next(self):
        if self.current_move < len(self.game.move_history)-1:
            self.current_move += 1

    def play_next(self, dt):
        if self.current_move < len(self.game.move_history)-1:
            self.current_move += 1
        else:
            Clock.unschedule(self.play_next)
            self.in_play = False

    def prev(self):
        if self.current_move > 0:
            self.current_move -= 1

    def play(self, obj):
        if not self.in_play:
            Clock.schedule_interval(self.play_next, 1.5)
            self.in_play = True
        else:
            Clock.unschedule(self.play_next)
            self.in_play = False


class GameInfo(BoxLayout):
    white = StringProperty('')
    black = StringProperty('')
    date = StringProperty('')
    moves = StringProperty('')
    event = StringProperty('')
    fen = StringProperty('')

def none(touch):
    pass

class GameWidgetScreen(Screen):
    def __init__(self, **kwargs):
        super(GameWidgetScreen, self).__init__(**kwargs)
        game = kwargs.get('game', None)
        self.add_widget(GameWidget(game=game))

class GameWidget(BoxLayout):
    # game = ObjectProperty()
    board_orientation = StringProperty('horizontal')
    initial_size = ListProperty()
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.game = kwargs.get('game', ScorebookGame())
        self.orientation = 'vertical'
        # self.board = Popup(content=ChessboardUI(game=app.game), title='Chessboard')
        self.board = AnchorLayout(size_hint=(None, None), anchor_x='left', anchor_y='bottom', height=dp(200), width=dp(200))

        self.move_list = AnchorLayout(size_hint=(None, None), anchor_x='right', anchor_y='top', height=dp(200), width=dp(200))
        lst = MoveList(game=self.game.game)
        lst.bind(current_move=self.change_to_move)
        self.move_list.add_widget(lst)

        self.board.board = ChessboardUI(game=self.game.game)
        self.board.board.actual_board.on_touch_down = none
        self.board.board.actual_board.on_touch_move = none
        self.board.board.actual_board.on_touch_up = none
        # self.board.add_widget(self.board.move_list)
        self.board.add_widget(self.board.board)
        # self.add_widget(self.board)

        nav = BoxLayout(size_hint_y=None, height=dp(50))
        b = Button(text="<< Games", size_hint_x=None, width=dp(100), background_normal='image/clear_white.png', color=(0,.5,0,1))
        b.bind(on_release=self.go_back)
        nav.add_widget(b)

        self.add_widget(nav)


        info_box = GameInfo(white=self.game.white,
                            black=self.game.black,
                            date=datetime.datetime.strptime(self.game.date, "%Y-%m-%d %H:%M:%S").strftime('%Y.%m.%d'),
                            round=self.game.round,
                            moves=str(int(ceil(len(self.game.moves_list)/2.0))),
                            event=self.game.event,
                            fen=str(self.game.game))


        moves_table=StackLayout(padding=dp(5), spacing=dp(5))
        for move in self.game.game.move_history:
            moves_table.add_widget(MoveLabel(text=move))
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

        self.grabbed = None

        #minimize
        self.board.height = self.board.width = dp(100)
        self.board.board.minimize = self.move_list.opacity = 0.0
        self.move_list.height = 0
        self.move_list.width = 0

        self.bind(size=self.change_orient)

    def go_back(self, obj):
        self.parent.parent.current = 'games'

    def change_to_move(self, obj, value):
        # print obj, value
        self.board.board.all_moves = self.game.game.move_history[:value+1]
        # print self.game.game.move_history
        # print self.game.game.move_history[:value]

    def on_touch_down(self, touch):
        if self.board.board.collide_point(*touch.pos):
            touch.grab(self.board.board)
            self.grabbed = self.board.board
            self.initial_size = self.grabbed.size
        else:
            super(GameWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):

        if self.grabbed:
            if self.board_orientation == 'horizontal':
                size = (self.initial_size[0]+(touch.y-touch.oy)*2)
                if size < self.height:
                    if size > dp(100):
                        self.board.height = self.board.width = size
                        self.board.board.minimize = size*1.0/self.height
                        self.move_list.opacity = size*1.0/self.height
                        self.move_list.height = self.board.height
                        self.move_list.width = self.width - self.height
                    else:
                        self.board.height = self.board.width = dp(100)
                        self.board.board.minimize = self.move_list.opacity = 0.0
                        self.move_list.height = 0
                        self.move_list.width = 0
                else:
                    self.board.height = self.board.width = self.height
                    self.board.board.minimize = self.move_list.opacity = 1.0
                    self.move_list.height = self.height
                    self.move_list.width = self.width - self.height

            else:
                size = (self.initial_size[1]+(touch.x-touch.ox)*2)
                if size < self.width:
                    if size > dp(100):
                        self.board.height = self.board.width = size
                        self.board.board.minimize = size*1.0/self.height
                        self.move_list.opacity = size*1.0/self.height
                        self.move_list.width = self.board.width
                        self.move_list.height = self.height - self.width
                    else:
                        self.board.height = self.board.width = dp(100)
                        self.board.board.minimize = self.move_list.opacity = 0.0
                        self.move_list.height = 0
                        self.move_list.width = 0
                else:
                    self.board.height = self.board.width = self.width
                    self.board.board.minimize = self.move_list.opacity = 1.0
                    self.move_list.width = self.width
                    self.move_list.height = self.height - self.width


    def on_touch_up(self, touch):
        if self.grabbed:
            touch.ungrab(self.grabbed)
            self.grabbed = None

    def change_orient(self, obj, size):
        # print self.board_orientation
        orientation = 'vertical' if self.height > self.width else 'horizontal'
        if self.board_orientation != orientation:
            self.board_orientation = orientation
            self.blank.orientation = self.board_orientation
            self.blank.children[0], self.blank.children[1] = self.blank.children[1], self.blank.children[0]