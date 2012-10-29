#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax

RED = -1
YELLOW = 1

class AlphaBetaPlayer(Player, minimax.Game):

    """Sarena Player.

    A state is a tuple (b, p) where p is the player to make a move and b
    the board.

    """

    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        # TODO: remove depth limitation
        return depth >= 1 or board.is_finished()

    def evaluate(self, board):
        score = board.get_score()

        # return score * self.player
        if score > 0:
            return self.player
        elif score < 0:
            return -self.player
        else:
            return 0 # draw


    def play(self, percepts, step, time_left):
        self.player = RED if step % 2 == 0 else YELLOW
        board = Board(percepts, invert=(self.player==YELLOW))
        return minimax.search(board, self)


if __name__ == "__main__":
    player_main(AlphaBetaPlayer())
