#!/usr/bin/env python3

import random

from sarena import *

class FastPlayer(Player):
    def play(self, percepts, step, time_left):
        board = Board(percepts)
        # always play first action
        for action in board.get_actions():
            return action

if __name__ == "__main__":
    player_main(FastPlayer())
