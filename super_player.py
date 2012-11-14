#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Benoit Daloze & Xavier de Ryckel'''

from sarena import *
from time import time

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
BACKSTAB = 5
MAYBE = 2

# TODO: remove
# def d(obj):
#     print(obj)
#     return obj

RANGE36 = range(36)
LIST37 = [0 for _ in range(37)]
SCORE = 36 # index in state

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
        state = LIST37[:]
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
        state[SCORE] = State.score(state)
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

    def gen_successors(state):
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
                            s = state[:]
                            s[i] = EMPTY_PILE
                            s[n] = (h, nbot, top)
                            s[SCORE] = State.incremental_score(state, i, n, s, arrows)
                            yield((i, n), s)
                    elif not arrows: # arrows around
                        # move and reverse i to neighbor place
                        s = state[:]
                        s[i] = EMPTY_PILE
                        s[n] = (height, top, bot)
                        s[SCORE] = State.incremental_score(state, i, n, s, arrows)
                        yield((i, n), s)

    def successors(state, player, depth_left):
        if depth_left == 1:
            return State.gen_successors(state)
        else:
            successors = list(State.gen_successors(state))
            successors.sort(key=lambda a_s: a_s[1][SCORE], reverse=(player==1))
            return successors

    def to_board_action(action):
        return (action[0]//6, action[0]%6, action[1]//6, action[1]%6)

    def is_finished(state):
        for _, _ in State.gen_successors(state):
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

    def score_at(state, i, arrows):
        height, bot, top = state[i]
        if height == 0:
            return 0
        if arrows: # on arrows
            if height == 4:
                # for any 4-tower, top color wins
                return SURE_THING * 4 * top
            else:
                no_neighbors = True
                for n in State.NEIGHBORS[i]:
                    if state[n] is not EMPTY_PILE:
                        no_neighbors = False
                        break
                if no_neighbors:
                    # for any tower with no neighbors, top color wins
                    return SURE_THING * height * top
                else: # height is 1-3, some neighbors
                    # bot is useless
                    # top can go over another pile
                    return MAYBE * top * height
        else: # on normal
            if height == 4:
                # for any 4-tower, bottom color wins (except if all neighbors around until EOG)
                return SURE_THING * 4 * bot
            else: # height is 1-3
                # (for any tower with no neighbors in range 2, bottom color wins => too rare)
                # bot will be ~ likely returned and win a tower
                return BACKSTAB * bot * height

    def score(state):
        score = 0
        for i, arrows in State.ARROWS:
            score += State.score_at(state, i, arrows)
        return score

    def incremental_score(old_state, i, n, new_state, arrows):
        """
        arrows = i is on arrows
        EMPTY_PILE at i in new_state
        height at n > 0
        Need to update i, n, and (i or n, which one is not on arrows)'s neighbors
        """
        narrows = not(arrows)
        score = old_state[SCORE]
        # remove i score (new score is 0)
        score -= State.score_at(old_state, i, arrows)

        if narrows: # neighbors of i have arrows and might have no more other piles around
            # n will be evaluated as one of these
            for neighbor in State.NEIGHBORS[i]:
                score -= State.score_at(old_state, neighbor, narrows)
                score += State.score_at(new_state, neighbor, narrows)
        else:
            # evaluate n
            score -= State.score_at(old_state, n, narrows)
            score += State.score_at(new_state, n, narrows)

        return score

# Minimax
inf = float("inf")

class MyTimeoutError(Exception):
    pass

def negamax(state, max_depth, stop_time):
    def rec(state, alpha, beta, depth, color):
        if stop_time and time() >= stop_time:
            raise MyTimeoutError()
        if depth == max_depth:
            return color * state[SCORE]
        if State.is_finished(state):
            SuperPlayer.saw_end_of_game = True
            return color * state[SCORE]
        val = -inf
        for a, s in State.successors(state, color, max_depth-depth):
            v = -rec(s, -beta, -alpha, depth+1, -color)
            if v >= beta:
                return v
            if v > alpha:
                alpha = v
        return alpha

    alpha = -inf
    action = None
    for a, s in State.successors(state, 1, 0):
        v = -rec(s, -inf, -alpha, 1, -1)
        if v > alpha:
            alpha = v
            action = a
    return action


MAX_STEPS = 35

# We are always the yellow player
class SuperPlayer(Player):
    saw_end_of_game = False

    def play(self, percepts, step, time_left):
        state = State.from_percepts(percepts)

        if time_left: # if time limited
            steps_left = max(MAX_STEPS-step, 1)
            time_for_this_step = time_left / steps_left
            stop_time = time() + time_for_this_step

            # iterative deepening to find appropriate depth
            depth = 2
            SuperPlayer.saw_end_of_game = False
            action = negamax(state, depth, stop_time)
            try:
                while not SuperPlayer.saw_end_of_game:
                    depth += 1
                    action = negamax(state, depth, stop_time)
            except MyTimeoutError:
                print(depth-1) # what we actually did
            else:
                print("End")
                print(depth)
        else:
            stop_time = None
            depth = 4
            action = negamax(state, depth, stop_time)

        return State.to_board_action(action)

if __name__ == "__main__":
    State.setup()
    player_main(SuperPlayer())
