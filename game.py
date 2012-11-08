#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main program for the Sarena game.
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

import logging
import time
import socket
import xmlrpc.client
import pickle
import traceback

from sarena import *


class TimeCreditExpired(Exception):
    """A player has expired its time credit."""


class Viewer(Player):

    """Interface for a Sarena viewer and human player."""

    def update(self, board, step, action):
        """Update the viewer with the given Board at step step."""
        pass

    def finished(self, board, steps, score, reason=""):
        """The game is finished.

        Attributes:
        board -- the final Board instance
        steps -- the number of steps played
        score -- the winner (<0: red, >0: yellow, 0: draw)
        reason -- a specific reason for the victory or "" if standard

        """
        pass

    def replay(self, trace):
        """Replay a game given its saved trace."""
        board = trace.get_initial_board()
        step = 0
        self.update(board, step, (0, 0, 0, 0))
        for action, t in trace.actions:
            time.sleep(t)
            step += 1
            board.play_action(action)
            self.update(board, step, action)
        self.finished(board, step, trace.score, trace.reason)


class ConsoleViewer(Viewer):

    """Simple console viewer."""

    def update(self, board, step, action):
        print("Step", step)
        print(board)

    def play(self, percepts, step, time_left):
        player = 2 - step % 2
        while True:
            try:
                line = input("Player %s plays (i1,j1,i2,j2): " % player)
            except EOFError:
                exit(1)
            try:
                action = [int(x.strip()) for x in line.split(",")]
                assert len(action) == 4
                return action
            except (ValueError, AssertionError):
                pass

    def finished(self, board, steps, score, reason=""):
        if score == 0:
            print("Draw game")
        else:
            if score < 0:
                print("Red",)
            else:
                print ("Yellow",)
            print("has won!")
        if reason:
            print("Reason:", reason)


class Trace:

    """Keep track of a played game.

    Attributes:
    time_limits -- a sequence of 2 elements containing the time limits in
        seconds for each player, or None for a time-unlimitted player
    invert -- whether the initial board was inverted
    actions -- list of tuples (action, time) of the played action. The first
        element is the action, the second one is the time taken in seconds.
    score -- score of the game
    reason -- specific reason for victory or "" if standard

    """

    def __init__(self, board, time_limits):
        """Initialize the trace.

        Arguments:
        board -- the initial board
        time_limits -- a sequence of 2 elements containing the time limits in
            seconds for each player, or None for a time-unlimitted player

        """
        self.time_limits = time_limits
        self.initial_board = board.get_percepts()
        self.max_height = board.max_height
        self.actions = []
        self.score = 0
        self.reason = ""

    def add_action(self, action, t):
        """Add an action to the trace.

        Arguments:
        action -- the played action, a tuple as specified by
            sarena.Board.play_action
        t -- a float representing the number of seconds the player has taken
            to generate the action

        """
        self.actions.append((action, t))

    def set_score(self, score, reason):
        """Set the winner.

        Arguments:
        score -- the score
        reason -- the specific reason of victory

        """
        self.score = score
        self.reason = reason

    def get_initial_board(self):
        """Return a Board instance representing the initial board."""
        return Board(self.initial_board)

    def write(self, filename):
        """Write the trace to a file."""
        f = None
        try:
            f = open(filename, "wb")
            pickle.dump(self, f)
        finally:
            if f is not None:
                f.close()


def load_trace(filename):
    """Load a trace from a file."""
    f = None
    try:
        f = open(filename, "rb")
        return pickle.load(f)
    finally:
        if f is not None:
            f.close()


def play_game(players, board, viewer=None, credits=[None, None]):
    """Play the Sarena game and return the trace as a Trace object.

    Arguments:
    players -- a sequence of 2 elements containing the players (instances
        of Player)
    board -- the board on which to play
    viewer -- the viewer or None if none should be used
    credits -- a sequence of 2 elements containing the time credit in seconds
        for each player, or None for a time-unlimitted player

    """
    if viewer is None:
        viewer = Viewer()
    logging.info("Starting new game")
    step = 0
    trace = Trace(board, credits)
    viewer.update(board, step, (0, 0, 0, 0))
    try:
        while not board.is_finished():
            player = step % 2
            step += 1
            logging.debug("Asking player %d to play step %d", player, step)
            if credits[player] is not None:
                logging.debug("Time left for player %d: %f", player,
                              credits[player])
                if credits[player] < 0:
                    raise TimeCreditExpired
                socket.setdefaulttimeout(credits[player] + 1)
            start = time.time()
            try:
                action = players[player].play(
                    board.get_percepts(player == 1),
                    step,
                    credits[player])
            except socket.timeout:
                credits[player] = -1.0  # ensure it is counted as expired
                raise TimeCreditExpired
            except (socket.error, xmlrpc.client.Fault) as e:
                logging.error("Player %d was unable to play step %d." +
                        " Reason: %s", player, step, e)
                traceback.print_tb(e.__traceback__)
                raise InvalidAction
            end = time.time()
            t = end - start
            logging.info("Step %d: received action %s in %fs",
                         step, action, t)
            if credits[player] is not None:
                credits[player] -= t
                logging.debug("New time credit for player %d: %f", player,
                              credits[player])
                if credits[player] < -0.5:  # small epsilon to be sure
                    raise TimeCreditExpired
            board.play_action(action)
            trace.add_action(action, t)
            viewer.update(board, step, action)
    except (TimeCreditExpired, InvalidAction) as e:
        if isinstance(e, TimeCreditExpired):
            logging.debug("Time credit expired")
            reason = "Opponent's time credit has expired."
        else:
            logging.debug("Invalid action: %s", e.action)
            reason = "Opponent has played an invalid action."
        if player == 0:
            score = -1
        else:
            score = 1
        step -= 1
    else:
        reason = ""
        score = board.get_score()
        logging.info("Score: %d", score)
    if score > 0:
        logging.info("Winner: player 1")
    elif score < 0:
        logging.info("Winner: player 2")
    else:
        logging.info("Winner: draw game")
    trace.set_score(score, reason)
    viewer.finished(board, step, score, reason)
    return trace


def connect_player(uri):
    """Connect to a remote player and return a proxy for the Player object."""
    return xmlrpc.client.ServerProxy(uri, allow_none=True)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options] player1 player2\n" +
                                "       %prog -r FILE",
                          description="Play the Sarena game." +
                          "A player is either a URI or the" +
                          " keyword 'human'.")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="be verbose")
    parser.add_option("-r", "--replay", dest="replay",
                      help="replay the trace written in FILE",
                      metavar="FILE")
    parser.add_option("-w", "--write", dest="write",
                      help="write the trace to FILE for replay with -r" +
                           " (no effect on replay)",
                      metavar="FILE")
    parser.add_option("--no-gui",
                      action="store_false", dest="gui", default=True,
                      help="do not try to load the graphical user interface")
    parser.add_option("--headless",
                      action="store_true", dest="headless", default=False,
                      help="run without user interface (players cannot be" +
                           " human)")
    g = parser.add_option_group("Rule options (no effect on replay)")
    g.add_option("-t", "--time", type=float, dest="time",
                 help="set the time credit per player (default: untimed game)",
                 metavar="SECONDS")
    g.add_option("--invert",
                 action="store_true", dest="invert", default=False,
                 help="invert the initial board")
    g.add_option("--board", dest="board",
                   help="load initial board from FILE", metavar="FILE")
    (options, args) = parser.parse_args()
    if options.time is not None and options.time <= 0:
        parser.error("option -t: time credit must be strictly positive")
    if options.replay is None and len(args) != 2:
        parser.error("need to specify two players")
    if options.replay is None and options.headless and \
            (args[0] == "human" or args[1] == "human"):
        parser.error("human players are not allowed in headless mode")
    if options.replay is not None and options.headless:
        parser.error("cannot replay in headless mode")

    level = logging.WARNING
    if options.verbose:
        level = logging.DEBUG
    logging.basicConfig(format="%(asctime)s -- %(levelname)s: %(message)s",
                        level=level)

    # Create initial board
    if options.replay is not None:
        # replay mode
        logging.info("Loading trace '%s'", options.replay)
        try:
            trace = load_trace(options.replay)
        except (IOError, pickle.UnpicklingError) as e:
            logging.error("Unable to load trace. Reason: %s", e)
            exit(1)
        board = trace.get_initial_board()
    elif options.board is not None:
        # load board
        logging.debug("Loading board from '%s'", options.board)
        try:
            percepts = load_percepts(options.board)
        except (IOError, pickle.UnpicklingError) as e:
            logging.warning("Unable to load board. Reason: %s", e)
            exit(1)
        board = Board(percepts)
    else:
        # default board
        board = Board(invert=options.invert)

    # Create viewer
    if options.headless:
        options.gui = False
        viewer = None
    else:
        if options.gui:
            try:
                import gui
                viewer = gui.TkViewer(board)
            except Exception as e:
                logging.warning("Unable to load GUI, falling back to" +
                        " console. Reason: %s", e)
                options.gui = False
        if not options.gui:
            viewer = ConsoleViewer()

    if options.replay is None:
        # Normal play mode
        players = [viewer, viewer]
        credits = [None, None]
        for i in range(2):
            if args[i] != 'human':
                players[i] = connect_player(args[i])
                credits[i] = options.time
        trace = [None]

        def play():
            try:
                trace[0] = play_game(players, board, viewer, credits)
            except KeyboardInterrupt:
                exit()
            if options.write is not None:
                logging.info("Writing trace to '%s'", options.write)
                try:
                    trace[0].write(options.write)
                except IOError as e:
                    logging.error("Unable to write trace. Reason: %s", e)
            if options.gui:
                logging.debug("Replaying trace.")
                viewer.replay(trace[0], show_end=True)

        if options.gui:
            import threading
            threading.Thread(target=play).start()
            viewer.run()
        else:
            play()
    else:
        # Replay mode
        logging.debug("Replaying trace.")
        viewer.replay(trace)
