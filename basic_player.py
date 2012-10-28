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
            yield None, (board, player*(-1))
        else:
            actions = board.get_actions()
            for action in actions:
                if(board.is_action_valid(action)):
                    board.play_action(action)
                    newboard = Board(board.get_percepts(True)) #instead of simply cloning, we create a new REVERSED board. Do we need to COPY the percepts or is it fine like that to create a NEW board ?
                    otherPlayer = player*(-1)
                    yield action, (newboard, otherPlayer) # (action, state)
            #do we need to yield None if there is no action or if all actions are not valid ?

    def cutoff(self, state, depth):
        board, player = state
        return board.is_finished()
        #anything to do with the player ? what to do with depth ?

    def evaluate(self, state):
        board, player = state
        score = board.get_score()

        if score > 0:
            if player == 1:
                return -1
            else:
                return 1
        if score < 0:
            if player == 1:
                return 1
            else:
                return -1
        else:
            return 0 #draw


    def play(self, percepts, step, time_left):
        if step % 2 == 0:
            player = -1
        else:
            player = 1
        state = (Board(percepts), player)
        return minimax.search(state, self)


if __name__ == "__main__":
    player_main(AlphaBetaPlayer())
