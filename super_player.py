#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax

# We are always the yellow player
class SuperPlayer(Player, minimax.Game):
    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        # TODO: remove depth limitation
        return depth >= 2 or board.is_finished()

    def score(board):
        score = 0
        m = board.m
        # final states:
        # for any 4-tower on arrows, top color wins
        # for i,j,s in board.get_towers():
        #     if (i,j) is arrows and height(tower) == 4:
        #         score += top color

        # for any 4-tower on normal, bottom color wins (except if all neighbors around until EOG)
        # for i,j,s in board.get_towers():
        #     if (i,j) is normal and height(tower) == 4:
        #         score += bottom color

        # for any tower with no neighbors on arrows, top color wins (except if any incoming around)
        # for i,j,s in board.get_towers():
        #     if (i,j) is arrows and no neighbors:
        #         score += top color / 2

        # for any tower with no neighbors on normal, bottom color wins (except if any incoming in range 2 ... not likely)

    def evaluate(self, board):
        return board.get_score()

    def play(self, percepts, step, time_left):
        board = Board(percepts)
        return minimax.search(board, self)

if __name__ == "__main__":
    player_main(SuperPlayer())
