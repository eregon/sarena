#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        # TODO

    def cutoff(self, state, depth):
        board, player = state
        # TODO

    def evaluate(self, state):
        board, player = state
        # TODO

    def play(self, percepts, step, time_left):
        if step % 2 == 0:
            player = -1
        else:
            player = 1
        state = (Board(percepts), player)
        return minimax.search(state, self)


if __name__ == "__main__":
    player_main(AlphaBetaPlayer())
