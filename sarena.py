# -*- coding: utf-8 -*-
"""
Common definitions for the Sarena players.
Copyright (C) 2012 - Cyrille Dejemeppe, Uclouvain
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
import pickle

def random_board():
    """Returns a random initial board."""
    tokens = [[1, -1],  [1, -1],  [1, -1],  [1, -1],  [1, -1],  [1, -1],
              [1, 2],  [1, 2],  [1, 2],  [1, 2],  [1, 2],  [1, 2],
              [1, 2],  [1, 2],  [1, 2],  [1, 2],  [1, 2],  [1, 2],
              [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],
              [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],  [-1, 2],
              [2, 2],  [2, 2],  [2, 2],  [2, 2],  [2, 2],  [2, 2]]
    random.shuffle(tokens)
    for token in tokens:
        random.shuffle(token)
    board = [[[[0 for l in range(2)] for k in range(5)]
              for i in range(6)] for j in range(6)]
    for i in range(6):
        for j in range(6):
            # When the cell contains arrows
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                board[i][j] = (4, tokens[(i * 6) + j], [0, 0], [0, 0], [0, 0])
                # When the cell is a classical one
            else:
                board[i][j] = (3, tokens[(i * 6) + j], [0, 0], [0, 0], [0, 0])
    return board


class InvalidAction(Exception):

    """Raised when an invalid action is played."""

    def __init__(self, action=None):
        self.action = action


class Board:

    """Representation of a Sarena Board.

    self.m is a self.rows by self.columns bi-dimensional array representing the
    board. The quintuple of a cell represents the circle and the tower on it.
    The first element of the quintuple is the type of the circle on the board
    (3 is for an classical circle, 4 is for a circle with arrows allowing to
    return a tower).
    The second to fifth element represent the tower put on the cell, the second
    element being the bottom of the tower while the fifth element is the top of
    the tower. In case a tower has a height smaller than 4, the elements of the
    tuple are set to 0 when they correspond to no token. The tokens are
    represented by pairs of integers being 1, -1 or 2. Each of these integers
    1 and -1 corresponds to the respective colors of player 1 (yellow) and
    player 2 (red) while integer 2 corresponds to the two neutral colors
    (grey). The first element of each pair corresponds to the bottom of the
    token while the second element is the top.

    """

    # standard sarena
    max_height = 4

    def __init__(self, percepts, invert=False):
        """Initialize the board.

        Arguments:
        percepts -- matrix representing the board
        invert -- whether to invert the sign of all values, inverting the
            players

        """
        self.m = percepts
        self.rows = len(self.m)
        self.columns = len(self.m[0])
        self.m = self.get_percepts(invert)  # make a copy of the percepts

    def __str__(self):
        def str_cell(i, j):
            if self.m[i][j][0] == 3:
                x = "[C,"
            else:
                x = "[I,"
            for k in range(1, 4):
                if self.m[i][j][k][0] == 0:
                    x += "===|"
                else:
                    if self.m[i][j][k][0] == -1:
                        c1 = "R"
                    elif self.m[i][j][k][0] == 1:
                        c1 = "Y"
                    else:
                        c1 = "N"
                    if self.m[i][j][k][1] == -1:
                        c2 = "R"
                    elif self.m[i][j][k][1] == 1:
                        c2 = "Y"
                    else:
                        c2 = "N"
                    x += "%s-%s|" % (c1, c2)
            if self.m[i][j][4][0] == 0:
                x += "===]"
            else:
                if self.m[i][j][4][0] == -1:
                    c1 = "R"
                elif self.m[i][j][4][0] == 1:
                    c1 = "Y"
                else:
                    c1 = "N"
                if self.m[i][j][4][1] == -1:
                    c2 = "R"
                elif self.m[i][j][4][1] == 1:
                    c2 = "Y"
                else:
                    c2 = "N"
                x += "%s-%s]" % (c1, c2)
            return x
        return "\n".join(" ".join(str_cell(i, j) for j in range(self.columns))
                         for i in range(self.rows))

    def clone(self):
        """Return a clone of this object."""
        return Board(self.m)

    def get_percepts(self, invert=False):
        """Return the percepts corresponding to the current state.

        If invert is True, the sign of all values is inverted to get the view
        of the other player.

        """
        newBoard = [[[[0 for i in range(2)] for j in range(5)]
                     for k in range(self.columns)] for l in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.columns):
                newBoard[i][j][0] = self.m[i][j][0]
                for k in range(1, 5):
                    for l in range(2):
                        if (invert and abs(self.m[i][j][k][l]) == 1):
                            newBoard[i][j][k][l] = -1 * self.m[i][j][k][l]
                        else:
                            newBoard[i][j][k][l] = self.m[i][j][k][l]
        return newBoard

    def get_towers(self):
        """Yield all towers.

        Yield the towers as triplets (i, j, s):
        i -- row number of the tower
        j -- column number of the tower
        s -- state of the tower (quintuple with
                                 first element being 3 if cell is classical
                                                     4 if cell contains arrows
                                 second to fifth element being numbers
                                  describing the stack of tokens
                                 constituting the tower)

        """
        for i in range(self.rows):
            for j in range(self.columns):
                if self.m[i][j]:
                    yield (i, j, self.m[i][j])

    def is_action_valid(self, action):
        """Return whether action is a valid action."""
        try:
            i1, j1, i2, j2 = action
            if i1 < 0 or j1 < 0 or i2 < 0 or j2 < 0 or \
               i1 >= self.rows or j1 >= self.columns or \
               i2 >= self.rows or j2 >= self.columns or \
               (i1 == i2 and j1 == j2) or (abs(i1 - i2) > 1) or \
               (abs(j1 - j2) > 1) or (abs(i1 - i2) + abs(j1 - j2) != 1):
                return False
            h1 = self.get_height(self.m[i1][j1])
            h2 = self.get_height(self.m[i2][j2])
            if h1 <= 0 or h1 > self.max_height or h2 < 0 or \
                    (h2 == 0 and self.m[i2][j2][0] != 4) or \
                    h2 >= self.max_height or h1 + h2 > self.max_height:
                return False
            return True
        except (TypeError, ValueError):
            return False

    def get_tower_actions(self, i, j):
        """Yield all actions with moving tower (i,j)"""
        h = self.get_height(self.m[i][j])
        if h > 0 and h <= self.max_height:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    action = (i, j, i + di, j + dj)
                    if (abs(di) + abs(dj) == 1) and \
                            self.is_action_valid(action):
                        yield action

    def is_tower_movable(self, i, j):
        """Return wether tower (i,j) is movable"""
        for action in self.get_tower_actions(i, j):
            return True
        return False

    def get_actions(self):
        """Yield all valid actions on this board."""
        for i, j, s in self.get_towers():
            for action in self.get_tower_actions(i, j):
                yield action

    def play_action(self, action):
        """Play an action if it is valid.

        An action is a 4-uple containing the row and column of the tower to
        move and the row and column of the tower to gobble. If the action is
        invalid, raise an InvalidAction exception. Return self.

        """
        if not self.is_action_valid(action):
            raise InvalidAction(action)
        i1, j1, i2, j2 = action
        h1 = self.get_height(self.m[i1][j1])
        h2 = self.get_height(self.m[i2][j2])
        # We move a tower on the top of another tower
        if h2 > 0:
            for k in range(1, h1 + 1):
                self.m[i2][j2][k + h2] = self.m[i1][j1][k]
        # We move a tower on an 'arrow-cell' and we invert it
        else:
            tmpTow = self.m[i1][j1][1:(h1 + 1)]
            for token in tmpTow:
                token.reverse()
            tmpTow.reverse()
            self.m[i2][j2][1:(h1 + 1)] = tmpTow
        self.m[i1][j1] = [self.m[i1][j1][0], [0, 0], [0, 0], [0, 0], [0, 0]]
        return self

    def is_finished(self):
        """Return whether no more moves can be made (i.e., game finished)."""
        for action in self.get_actions():
            return False
        return True

    def get_score(self):
        """Return a score for this board.

        The score is the difference between the number of towers of each
        player. In case of ties, it is the difference between the maximal
        height towers of each player. If self.is_finished() returns True,
        this score represents the winner (<0: red, >0: yellow, 0: draw).

        """
        score = 0
        for i in range(self.rows):
            for j in range(self.columns):
                tower = self.get_tower(self.m[i][j])
                if tower:
                    if tower[-1][1] == -1:
                        score -= len(tower)
                    elif tower[-1][1] == 1:
                        score += len(tower)
        if score == 0:
            for i in range(self.rows):
                for j in range(self.columns):
                    tower = self.get_tower(self.m[i][j])
                    if tower:
                        if tower[-1][1] == -1:
                            for half_tok in filter(lambda token:
                                                       (token[0] == -1 or
                                                        token[1] == -1),
                                                   tower):
                                score -= 1
                        elif tower[-1][1] == 1:
                            for half_tok in filter(lambda token:
                                                       (token[0] == 1 or
                                                        token[1] == 1),
                                                   tower):
                                score += 1
        return score

    def get_height(self, tower):
        height = 0
        for e in filter(lambda e: e != [0, 0], tower[1:]):
            height += 1
        return height

    def get_tower(self, tower):
        height = self.get_height(tower)
        newTow = []
        for i in range(1, height + 1):
            newTow.append(tower[i])
        return newTow

    def write(self, filename):
        """Write the board to a file."""
        f = None
        try:
            f = open(filename, "wb")
            pickle.dump(self.m, f)
        finally:
            if f is not None:
                f.close()

def load_percepts(pickleFile):
    """Load percepts from a pickle file.

    """
    f = None
    try:
        f = open(pickleFile, mode="rb")
        return pickle.load(f)
    finally:
        if f is not None:
            f.close()


class Player:

    """Interface for a Sarena player"""

    def play(self, percepts, max_height, step, time_left):
        """Play and return an action.

        Arguments:
        percepts -- the current board in a form that can be fed to the Board
            constructor. The board is always viewed from the perspective that
            this player is the yellow one, i.e., he has the positive numbers.
        max_height -- the maximum height of a tower
        step -- the current step number, starting from 1
        time_left -- a float giving the number of seconds left from the time
            credit for this player. If the game is not time-limited, time_left
            is None.

        """
        pass


def serve_player(player, address, port):
    """Serve player on specified bind address and port number."""
    from xmlrpc.server import SimpleXMLRPCServer
    server = SimpleXMLRPCServer((address, port))
    server.register_instance(player)
    print("Listening on " + address + ":" + str(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def player_main(player, options_cb=None, setup_cb=None):
    """Launch player server depending on arguments.

    Arguments:
    player -- a Player instance
    options_cb -- function taking two arguments: the player and an
        OptionParser. It can add custom options to the parser.
        (None to disable)
    setup_cb -- function taking three arguments: the player, the OptionParser
        and the options dictionary. It can be used to configure the player
        based on the custom options. (None to disable)

    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--bind", dest="address", default="",
                      help="bind to address ADDRESS (default: all addresses)")
    parser.add_option("-p", "--port", type="int", dest="port", default=8000,
                      help="set port number (default: %default)")
    if options_cb is not None:
        options_cb(player, parser)
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("no arguments needed")
    if options.port < 1 or options.port > 65535:
        parser.error("option -p: invalid port number")
    if setup_cb is not None:
        setup_cb(player, parser, options)
    serve_player(player, options.address, options.port)
