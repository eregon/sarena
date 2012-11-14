'''Benoit Daloze & Xavier de Ryckel'''

from sarena import *
import minimax

class AlphaBetaPlayer(Player, minimax.Game):
    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        return True

    def evaluate(self, board):
        return board.get_score()

    def play(self, percepts, step, time_left):
        # We are always the yellow player
        board = Board(percepts)
        return minimax.search(board, self)

if __name__ == "__main__":
    player = AlphaBetaPlayer()
    player_main(player)
