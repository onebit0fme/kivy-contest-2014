__author__ = 'onebit0fme'
from Chessnut.game import Game

chessgame = Game()
print chessgame  # 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

print chessgame.get_moves()
print
chessgame.apply_move('e2e4')  # succeeds!
chessgame.apply_move('c7c5')  # succeeds!
chessgame.apply_move('g1f3')  # succeeds!
chessgame.apply_move('d7d6')  # succeeds!
print chessgame  # 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
print chessgame.board._position
print chessgame.move_history
chessgame.move_history.pop(-1)
print chessgame.board._position
print chessgame.move_history


# chessgame.apply_move('e2e4')  # fails! (raises InvalidMove exception)