#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *
import minimax

NO_CHIP_TUPLE = [0,0]

# a cell is represented as
# ttbb0hhh
# with:
# tt: color on top of the pile
# bb: color on bottom of the pile
# hhh: height of the pile, represented on 3 bytes

HEIGHT_MASK = 0b00000111
BOT_MASK    = 0b00110000
TOP_MASK    = 0b11000000

BOT_OFFSET = 4
TOP_OFFSET = 6
DELTA_OFFSET = TOP_OFFSET-BOT_OFFSET

# colors
# careful choice of values
# second bit means a player (self or opponent)
# value of player for score is color-2
PLAYER_MASK   = 0b01
SELF_COLOR    = 0b01
OTHER_COLOR   = 0b11
NEUTRAL_COLOR = 0b10
NO_CHIP_COLOR = 0b00

# an empty tower is represented as
EMPTY_PILE = 0b00000000

# TODO: remove
# def d(obj):
#     print(obj)
#     return obj

class State:
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
        state = bytearray(36)
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
                    state[k] = height + (bot << BOT_OFFSET) + (top << TOP_OFFSET)

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
                e & HEIGHT_MASK,
                State.color_code_to_letter((e & BOT_MASK) >> BOT_OFFSET),
                State.color_code_to_letter((e & TOP_MASK) >> TOP_OFFSET)
            ) for e in row) + "\n"
        return s

    def neighbors(state, i):
        if i >= 6:     # NORTH
            yield(i-6, state[i-6])
        if i % 6 != 5: # EAST
            yield(i+1, state[i+1])
        if i < 30:     # SOUTH
            yield(i+6, state[i+6])
        if i % 6 != 0: # WEST
            yield(i-1, state[i-1])

    def successors(state):
        for i in range(36): # for i, pile in enumerate(state):
            pile = state[i]
            if pile: # if any height
                arrows = (i % 2 == (i // 6) % 2) # x % 2 == y % 2
                height = (pile & HEIGHT_MASK)
                for n, neighbor in State.neighbors(state, i):
                    if neighbor:
                        h = height + (neighbor & HEIGHT_MASK)
                        if h <= 4:
                            # put i on top of neighbor
                            new_state = bytearray(state)
                            new_state[i] = EMPTY_PILE
                            new_state[n] = h + (neighbor & BOT_MASK) + (pile & TOP_MASK)
                            yield((i//6, i%6, n//6, n%6), new_state)
                    elif not arrows: # arrows around
                        # move and reverse i to neighbor place
                        new_state = bytearray(state)
                        new_state[i] = EMPTY_PILE
                        new_state[n] = height + ((pile & TOP_MASK) >> DELTA_OFFSET) + \
                                                ((pile & BOT_MASK) << DELTA_OFFSET)
                        yield((i//6, i%6, n//6, n%6), new_state)

    def is_finished(state):
        for action, state in State.successors(state):
            return False
        return True

    def score(state):
        score = 0
        for i in range(36):
            pile = state[i]
            if pile:
                color = (pile & TOP_MASK) >> TOP_OFFSET
                if color == SELF_COLOR:
                    score += (pile & HEIGHT_MASK)
                elif color == OTHER_COLOR:
                    score -= (pile & HEIGHT_MASK)
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
    player_main(SuperPlayer())
