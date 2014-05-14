__author__ = 'onebit0fme'
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, BooleanProperty, StringProperty
from kivy.metrics import dp
from kivy.lang import Builder
from Chessnut.game import Game, InvalidMove

Builder.load_string('''
<ChessboardUI>:
    canvas:
        Color:
            rgba: (1,1,1,root.minimize)
        Rectangle:
            pos: self.pos
            size: self.size

<Chessboard>:
    cols: 8
    rows: 8

<ChessboardGrid>:
    canvas:
        Color:
            rgb: (0,.5,0)
        Line:
            rectangle: self.pos[0], self.pos[1], self.size[0], self.size[1]
            width: dp(2)
    cols: 8
    rows: 8

<BoardCell>:

<BoardCellBG>:
    canvas.before:
        Color:
            rgb: (0,.5,0) if root.black else (1,1,1)
        Rectangle:
            pos: self.pos
            size: self.size
#            source: 'image/primary.png' if root.black else 'image/clear_white.png'


<Chessman>:
    Image:
        source: 'image/'+root.symbol+'.png'
        size_hint: (.8,.8)

<GridLabel>:
    color: (0,0,0,1)

<GridLabelOpponent>:
    Scatter:
        rotation: 180
        do_rotation: False
        do_scale: False
        do_translation: False
        Label:
            size: root.size
            text_size: root.size
            valign: 'middle'
            halign: 'center'
            text: root.text
            color: (0,0,0,1)
''')

class GridLabelOpponent(BoxLayout):
    '''
    Upside-down label
    '''
    text = StringProperty('')
    def __init__(self, **kwargs):
        super(GridLabelOpponent, self).__init__(**kwargs)

class GridLabel(Label):
    pass

class BoardCell(BoxLayout):
    name = StringProperty('')

class BoardCellBG(BoxLayout):
    name = StringProperty('')
    black = BooleanProperty(False)

class Chessman(BoxLayout):
    symbol = StringProperty(' ')

class ChessboardUI(BoxLayout):
    '''
    Complete interface for chessboard
    NOTE: the 'game' has to be passed along, as well as returned back to synchronize with other widgets
    '''
    minimize = NumericProperty(1.0)
    all_moves = ListProperty()
    move_made = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(ChessboardUI, self).__init__(**kwargs)
        game = kwargs.get('game', None)

        # left numbers
        left_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(30))
        for n in range(8, -1, -1):
            if n == 0:
                left_box.add_widget(Label())
                break
            left_box.add_widget(Label(text=str(n), color=(0,0,0,1)))

        # right numbers
        right_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(30))
        for n in range(8, -1, -1):
            if n == 0:
                right_box.add_widget(Label(size_hint_y=None, height=dp(30)))
                break
            right_box.add_widget(GridLabelOpponent(text=str(n), color=(0,0,0,1)))


        main_box = BoxLayout(orientation='vertical')

        merge_layers = RelativeLayout()
        background_grid = ChessboardGrid()
        self.actual_board = Chessboard(game=game)
        self.actual_board.bind(move_made=self.set_moves)
        merge_layers.add_widget(background_grid)
        merge_layers.add_widget(self.actual_board)


        bottom_box = BoxLayout(size_hint_y=None, height=dp(30))
        for c in ('a','b','c','d','e','f','g','h'):
            bottom_box.add_widget(Label(text=c, color=(0,0,0,1)))

        top_box = BoxLayout(size_hint_y=None, height=dp(30))
        for c in ('','a','b','c','d','e','f','g','h',''):
            if not c:
                top_box.add_widget(Label(size_hint_x=None, width=dp(30)))
                continue
            top_box.add_widget(GridLabelOpponent(text=c))

        main_box.add_widget(merge_layers)
        main_box.add_widget(bottom_box)

        except_top = BoxLayout()

        except_top.add_widget(left_box)
        except_top.add_widget(main_box)
        except_top.add_widget(right_box)

        self.orientation = 'vertical'
        self.add_widget(top_box)
        self.add_widget(except_top)

        self.labels = [bottom_box, top_box, left_box, right_box]
        self.bind(minimize=self.min, all_moves=self.change_board_moves)

    def set_moves(self, obj, made):
        self.move_made = made

    def change_board_moves(self, obj, moves):
        self.actual_board.change_game(moves)

    def min(self,obj, d):
        '''
        Change the size and opacity of the grid labels on minimizing
        '''
        if d < .4:
            d = 0.0
        for i in self.labels:
            i.opacity = d
        self.labels[0].height = dp(30)*self.minimize
        self.labels[1].height = dp(30)*self.minimize
        self.labels[2].width = dp(30)*self.minimize
        self.labels[3].width = dp(30)*self.minimize

    # def minimz(self, obj):
    #     print 'minimizing'
    #     self.parent.height = self.parent.width = dp(200)

class ChessboardGrid(GridLayout):
    '''
    Basically just a background to the chessboard.
    (background image would not look sharp enough)
    '''
    def __init__(self, **kwargs):
        super(ChessboardGrid, self).__init__(**kwargs)
        for i in range(64):
            if i%16 >= 8:
                if i%2 == 0:
                    cell = BoardCellBG(black=True)
                else:
                    cell = BoardCellBG() # white
            else:
                if i%2 == 0:
                    cell = BoardCellBG() # white
                else:
                    cell = BoardCellBG(black=True)
            self.add_widget(cell)

class Chessboard(GridLayout):
    '''
    Actual chessboard with moving pieces
    '''
    # all_moves = ListProperty()
    game = ObjectProperty()
    move_made = BooleanProperty(False)
    # for menu!
    go_to = StringProperty('')
    def __init__(self, **kwargs):
        super(Chessboard, self).__init__(**kwargs)
        self.game = kwargs.get('game', None)
        if self.game:
            board = self.game.board._position
            for row in ('8','7','6','5','4','3','2','1'):
                for col in ('a','b','c','d','e','f','g','h'):
                    cell = BoardCell(name=col+row)
                    self.add_widget(cell)
            for n, cell in enumerate(self.children):
                i = 63 - n
                if board[i] != ' ':
                    man = Chessman(symbol=board[i])
                    cell.add_widget(man)

        self.grabbed = None

        # when move history changes
        # self.bind(all_moves=self.change_game)

    def change_game(self, all_moves):
        # reset game
        # if self.game:
        #     self.game.reset()
        # else:
        self.game = Game()

        # apply move history
        for move in all_moves:
            self.game.apply_move(move)
        # print self.game.move_history
        # print self.game.board
        # populate new position
        board = self.game.board._position
        for n, cell in enumerate(self.children):
            cell.clear_widgets()
            i = 63 - n
            if board[i] != ' ':
                man = Chessman(symbol=board[i])
                cell.add_widget(man)

    def update(self):
        board = self.game.board._position
        for n, cell in enumerate(self.children):
            cell.clear_widgets()
            i = 63 - n
            if board[i] != ' ':
                man = Chessman(symbol=board[i])
                cell.add_widget(man)

    def on_touch_down(self, touch):
        for cell in self.children:
            if cell.collide_point(*touch.pos):
                if cell.children:
                    self.move_start = cell.name
                    # print self.move_start
                    self.grabbed = cell.children[0]
                    # print self.grabbed.parent
                    touch.grab(self.grabbed)

    def on_touch_move(self, touch):
        if self.grabbed:
            self.grabbed.pos = [touch.x-self.grabbed.size[0]/2, touch.y-self.grabbed.size[1]/2]

    def on_touch_up(self, touch):
        for cell in self.children:
            if cell.collide_point(*touch.pos) and self.grabbed:
                self.destination = cell.name
                try:
                    self.game.apply_move(self.move_start+self.destination)
                    print "Is Legal"
                    self.grabbed.parent.clear_widgets()
                    cell.clear_widgets()
                    cell.add_widget(self.grabbed)
                    # self.grabbed.pos = cell.pos
                    self.move_made = False if self.move_made else True
                    self.update()
                except InvalidMove:
                    print 'Not Legal Move'
                    self.grabbed.pos = self.grabbed.parent.pos

        if self.grabbed:
            touch.ungrab(self.grabbed)
            self.grabbed = None

