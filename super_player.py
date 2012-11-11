#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

import random

from sarena import *

NO_CHIP_TUPLE = [0,0]

# a cell is represented as
# (height, bot, top)

# colors
SELF_COLOR    =  1
OTHER_COLOR   = -1
NEUTRAL_COLOR =  0

# an empty tower is represented as
EMPTY_PILE = (0, 0, 0)

# a reversible action is represented as
# (from, to, pile_from, pile_to, new_pile)

# score
SURE_THING = 10
BACKSTAB = 4
MAYBE = 2
LOST = -1

# TODO: remove
# def d(obj):
#     print(obj)
#     return obj

RANGE36 = range(36)

class State:
    NEIGHBORS = None
    ARROWS = tuple(enumerate([i % 2 == (i // 6) % 2 for i in RANGE36])) # x % 2 == y % 2

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
        State.NEIGHBORS = [tuple(State.neighbors_at(i)) for i in RANGE36]

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
        state = list(RANGE36)
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

    def color_code_to_letter(height, color):
        if height == 0:
            return ' '
        elif color == SELF_COLOR:
            return 'Y'
        elif color == OTHER_COLOR:
            return 'R'
        elif color == NEUTRAL_COLOR:
            return 'N'

    def __repr__(state):
        s = ""
        for i in range(6):
            row = state[i*6:(i+1)*6]
            s += ' '.join("%d%s%s" % (
                h,
                State.color_code_to_letter(h, b),
                State.color_code_to_letter(h, t)
            ) for h,b,t in row) + "\n"
        return s

    def successors(state):
        for i, arrows in State.ARROWS:
            pile = state[i]
            height, bot, top = pile
            if height: # if any height
                for n in State.NEIGHBORS[i]:
                    neighbor = state[n]
                    nheight, nbot, ntop = neighbor
                    if nheight:
                        h = height + nheight
                        if h <= 4:
                            # put i on top of neighbor
                            yield(i, n, pile, neighbor, (h, nbot, top))
                    elif not arrows: # arrows around
                        # move and reverse i to neighbor place
                        yield(i, n, pile, EMPTY_PILE, (height, top, bot))

    def to_board_action(action):
        return (action[0]//6, action[0]%6, action[1]//6, action[1]%6)

    def is_finished(state):
        for _ in State.successors(state):
            return False
        return True

    def board_score(state):
        score = 0
        for i in RANGE36:
            height, _, top = state[i]
            score += height * top
        return score

    def fast_score(state):
        score = 0
        for i, arrows in State.ARROWS:
            height, bot, top = state[i]
            if arrows:
                score += height * top
            else:
                score += height * bot
        return score

    def score(state):
        score = 0
        for i, arrows in State.ARROWS:
            height, bot, top = state[i]
            if height > 0:
                if arrows: # on arrows
                    if height == 4:
                        # for any 4-tower, top color wins
                        score += SURE_THING * 4 * top
                    else:
                        no_neighbors = True
                        for n in State.NEIGHBORS[i]:
                            if n is not EMPTY_PILE:
                                no_neighbors = False
                                break
                        if no_neighbors:
                            # for any tower with no neighbors, top color wins
                            score += SURE_THING * height * top
                            # maybe count bot as LOST?
                        else: # height is 1-3, some neighbors
                            # bot is useless
                            score += LOST * bot
                            # top can go over another pile
                            score += MAYBE * top # * height ?
                else: # on normal
                    if height == 4:
                        # for any 4-tower, bottom color wins (except if all neighbors around until EOG)
                        score += SURE_THING * 4 * bot
                    else: # height is 1-3
                        # (for any tower with no neighbors in range 2, bottom color wins => too rare)
                        # bot will be ~ likely returned and win a tower
                        score += BACKSTAB * bot
                        # top is useless
                        score += LOST * top

        return score

# Minimax
inf = float("inf")

def negamax(state, max_depth):
    def rec(alpha, beta, depth, color):
        if depth >= max_depth or State.is_finished(state):
            return color * State.score(state)
        val = -inf
        for a in State.successors(state):
            i, n, pile, neighbor, new_pile = a
            state[i] = EMPTY_PILE
            state[n] = new_pile
            v = -rec(-beta, -alpha, depth+1, -color)
            state[i] = pile
            state[n] = neighbor
            if v >= beta:
                return v
            if v > alpha:
                alpha = v
        return alpha

    alpha = -inf
    action = None
    for a in State.successors(state):
        i, n, pile, neighbor, new_pile = a
        state[i] = EMPTY_PILE
        state[n] = new_pile
        v = -rec(-inf, -alpha, 1, -1)
        state[i] = pile
        state[n] = neighbor
        if v > alpha:
            alpha = v
            action = a
    return action

# We are always the yellow player
class SuperPlayer(Player):
    def play(self, percepts, step, time_left):
        # TODO: check step to see if need to reset
        state = State.from_percepts(percepts)
        action = negamax(state, 2)
        return State.to_board_action(action)

if __name__ == "__main__":
    State.setup()
    player_main(SuperPlayer())
