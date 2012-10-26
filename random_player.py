#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dummy random Sarena player.
Copyright (C) 2012 - Cyrille Dejemeppe, UCLouvain
Some inspiration was taken from code by Vianney Le Clément.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import random

from sarena import *


class RandomPlayer(Player):

    """A dumb random Sarena player."""

    def play(self, percepts, step, time_left):
        b = Board(percepts)
        return random.choice(list(b.get_actions()))


if __name__ == "__main__":
    player_main(RandomPlayer())
