#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax

NO_CHIP_TUPLE = [0,0]

# a cell is represented as
# (height, bot, top)

# colors
SELF_COLOR    =  1
OTHER_COLOR   = -1
NEUTRAL_COLOR =  0

# an empty tower is represented as
EMPTY_PILE = (0, 0, 0)

# TODO: remove
# def d(obj):
#     print(obj)
#     return obj

class State:
    NEIGHBORS = None

    def neighbors_at(i):
        if i >= 6:     # NORTH
            yield(i-6)
        if i % 6 != 5: # EAST
            yield(i+1)
        if i < 30:     # SOUTH
            yield(i+6)
        if i % 6 != 0: # WEST
            yield(i-1)

    def precompute_neighbors():
        State.NEIGHBORS = [tuple(State.neighbors_at(i)) for i in range(36)]

    def setup():
        State.precompute_neighbors()

    def color_code_from_board_color(color):
        if color == 1:
            return SELF_COLOR
        elif color == -1:
            return OTHER_COLOR
        elif color == 2:
            return NEUTRAL_COLOR
        else:
            raise Exception("Unknown board color: %d" % (color,))

    def from_percepts(percepts):
        state = list(range(36))
        for i in range(6):
            for j in range(6):
                k = i*6+j
                tower = percepts[i][j][1:]
                try:
                    height = tower.index(NO_CHIP_TUPLE)
                except ValueError:
                    height = 4
                if height == 0:
                    state[k] = EMPTY_PILE
                else:
                    top = State.color_code_from_board_color(tower[height-1][1])
                    bot = State.color_code_from_board_color(tower[0][0])
                    state[k] = (height, bot, top)

        # d(State.__repr__(state))
        return state

    def color_code_to_letter(color):
        if color == SELF_COLOR:
            return 'Y'
        elif color == OTHER_COLOR:
            return 'R'
        elif color == NEUTRAL_COLOR:
            return 'N'
        else:
            return ' '

    def __repr__(state):
        s = ""
        for i in range(6):
            row = state[i*6:(i+1)*6]
            s += ' '.join("%d%s%s" % (
                h,
                State.color_code_to_letter(b),
                State.color_code_to_letter(t)
            ) for h,b,t in row) + "\n"
        return s

    def successors(state):
        for i in range(36): # for i, pile in enumerate(state):
            height, bot, top = state[i]
            if height: # if any height
                arrows = (i % 2 == (i // 6) % 2) # x % 2 == y % 2
                for n in State.NEIGHBORS[i]:
                    nheight, nbot, ntop = state[n]
                    if nheight:
                        h = height + nheight
                        if h <= 4:
                            # put i on top of neighbor
                            new_state = state[:]
                            new_state[i] = EMPTY_PILE
                            new_state[n] = (h, nbot, top)
                            yield((i//6, i%6, n//6, n%6), new_state)
                    elif not arrows: # arrows around
                        # move and reverse i to neighbor place
                        new_state = state[:]
                        new_state[i] = EMPTY_PILE
                        new_state[n] = (height, top, bot)
                        yield((i//6, i%6, n//6, n%6), new_state)

    def is_finished(state):
        for action, state in State.successors(state):
            return False
        return True

    def score(state):
        score = 0
        for i in range(36):
            height, bot, top = state[i]
            score += height * top
        return score

# We are always the yellow player
class SuperPlayer(Player, minimax.Game):
    def successors(self, state):
        return State.successors(state)

    def cutoff(self, state, depth):
        # TODO: remove depth limitation
        return depth >= 3 or State.is_finished(state)

    def score(state):
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

    def evaluate(self, state):
        return State.score(state)

    def play(self, percepts, step, time_left):
        # TODO: check step to see if need to reset
        state = State.from_percepts(percepts)
        action = minimax.search(state, self)
        return action

if __name__ == "__main__":
    State.setup()
    player_main(SuperPlayer())
