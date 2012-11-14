#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax
import time

class AlphaBetaPlayer(Player, minimax.Game):
    def __init__(self):
        self.nodes = 0

    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            self.nodes += 1
            yield action, new_board

    def cutoff(self, board, depth):
        # TODO: remove depth limitation
        return depth >= 2 or board.is_finished()

    def evaluate(self, board):
        score = board.get_score()

        # return score
        if score > 0:
            return 1
        elif score < 0:
            return -1
        else:
            return 0 # draw


    def play(self, percepts, step, time_left):
        # We are always the yellow player
        board = Board(percepts)
        nodes_before = self.nodes
        t0 = time.clock()
        result = minimax.search(board, self)
        # result = minimax.search(board, self, prune=False)
        t1 = time.clock()
        print("Nodes visited:", self.nodes-nodes_before);
        print("Time required:", t1-t0)
        print("Result: ", result)
        return result

if __name__ == "__main__":
    player = AlphaBetaPlayer()
    player_main(player)
    print("Total number of nodes visited:", player.nodes)
