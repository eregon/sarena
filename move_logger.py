#!/usr/bin/env python3

import random
from sarena import *

class MoveLogger(Player):
    def __init__(self):
        self.log = open('moves.log', 'a')
    
    def play(self, percepts, step, time_left):
        if step == 1: # first step
            self.log.write('New Game\n')
            self.log.flush()
        b = Board(percepts)
        moves = list(b.get_actions())
        self.log.write('%d moves at step %d\n' % (len(moves), step))
        self.log.flush()
        return random.choice(moves)


if __name__ == "__main__":
    player_main(MoveLogger())
