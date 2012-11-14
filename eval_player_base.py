'''Benoit Daloze & Xavier de Ryckel'''

from sarena import *
import minimax

class EvalPlayerBase(Player, minimax.Game):
    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        return depth == 1

    def evaluate(self, board):
        return board.get_score()

    def play(self, percepts, step, time_left):
        # We are always the yellow player
        board = Board(percepts)
        return minimax.search(board, self)

if __name__ == "__main__":
    player = EvalPlayerBase()
    player_main(player)
