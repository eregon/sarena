#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax


class AlphaBetaPlayer(Player, minimax.Game):

    """Sarena Player.

    A state is a tuple (b, p) where p is the player to make a move and b
    the board.

    """

    def successors(self, state):
        board, player = state
        if board.is_finished():
            yield None, (board, -player)
        else:
            for action in board.get_actions():
                # copies the percepts, in the view of the opponent
                new_board = Board(board.m, invert=True)
                new_board.play_action(action)
                yield action, (new_board, -player) # (action, state)

    def cutoff(self, state, depth):
        board, player = state
        return board.is_finished()

    def evaluate(self, state):
        board, player = state
        score = board.get_score()

        if score > 0:
            return -player
        elif score < 0:
            return player
        else:
            return 0 # draw


    def play(self, percepts, step, time_left):
        if step % 2 == 0:
            player = -1
        else:
            player = 1
        state = (Board(percepts), player)
        return minimax.search(state, self)


if __name__ == "__main__":
    player_main(AlphaBetaPlayer())
