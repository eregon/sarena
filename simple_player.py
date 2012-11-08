#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax

# We are always the yellow player
class SimplePlayer(Player, minimax.Game):
    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        # TODO: remove depth limitation
        return depth >= 3 or board.is_finished()

    def evaluate(self, board):
        return board.get_score()

    def play(self, percepts, step, time_left):
        board = Board(percepts)
        return minimax.search(board, self)

if __name__ == "__main__":
    player_main(SimplePlayer())
