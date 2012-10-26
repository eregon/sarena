# -*- coding: utf-8 -*-
"""
Graphical user interface for the Sarena game.
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

import threading
from tkinter import *
from tkinter.font import Font

from sarena import *
from game import Viewer


class TkViewer(Viewer):

    """Graphical viewer using Tk."""

    w = 130  # size of a cell
    ratio_yx = 4.0 / 5.0  # ratio y/x
    r_cell_x = 3 * w / 7  # radius of a cell along x-axis
    r_cell_y = ratio_yx * r_cell_x  # radius of a cell along y-axis
    r_token_x = 2 * r_cell_x / 3  # radius of a token along x-axis
    r_token_y = ratio_yx * r_token_x  # radius of a token along y-axis
    dist_arrow_x1 = 3 * r_cell_x / 5  # measure to draw the arrows on circles
    dist_arrow_x2 = 11 * r_cell_x / 12  # measure to draw the arrows on circles
    dist_arrow_y = r_cell_y / 2  # measure to draw the arrows on circles
    dist_tokens = (r_cell_y - r_token_y) / 4  # the distance between two tokens

    def __init__(self, board):
        """Create a GUI viewer.

        Arguments:
        board -- initial board (a Board instance)

        """
        self.board = board
        self.canvas_width = self.w * board.columns
        self.canvas_height = self.w * board.rows * self.ratio_yx
        self.barrier = threading.Event()
        self.root = Tk()
        self.root.title("Sarena")
        self.root.resizable(False, False)
        self.root.bind_all("<Escape>", self.close)
        self.font = Font(size=16)
        self.canvas = Canvas(self.root, width=self.canvas_width,
                             height=self.canvas_height,
                             selectbackground="light gray")
        self.canvas.pack()
        # tower_ids is filled by _update_gui
        self.tower_ids = [[0 for j in range(self.board.columns)]
                          for i in range(self.board.rows)]
        self.cell_ids = [[0 for j in range(self.board.columns)]
                          for i in range(self.board.rows)]
        for i, j, h in self.board.get_towers():
            y = (i + .5) * self.w * self.ratio_yx
            x = (j + .5) * self.w
            color = ""
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                color = "black"
            else:
                color = "white"
            o = self.canvas.create_oval(x - self.r_cell_x, y - self.r_cell_y,
                                    x + self.r_cell_x, y + self.r_cell_y,
                                    width=1, outline="black", fill=color)
            self.canvas.create_text(x, y, text=str(""), font=self.font,
                                    tags=["cells"])
            if color == "black":
                self.canvas.create_line(x - self.dist_arrow_x1,
                                        y - self.dist_arrow_y,
                                        x - self.dist_arrow_x2,
                                        y,
                                        x - self.dist_arrow_x1,
                                        y + self.dist_arrow_y,
                                        arrow="last",
                                        fill="saddle brown",
                                        smooth="true",
                                        width=5.0,
                                        splinesteps=10)
                self.canvas.create_line(x + self.dist_arrow_x1,
                                        y + self.dist_arrow_y,
                                        x + self.dist_arrow_x2,
                                        y,
                                        x + self.dist_arrow_x1,
                                        y - self.dist_arrow_y,
                                        arrow="last",
                                        fill="saddle brown",
                                        smooth="true",
                                        width=5.0,
                                        splinesteps=10)
            self.cell_ids[i][j] = o
        self.status = Label(self.root, height=2, justify=LEFT)
        self.status.pack(side=LEFT)
        self.status_text = ""
        self.substatus_text = ""
        self.running = False

    def run(self):
        """Launch the GUI."""
        if self.running:
            return
        self.running = True
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        # ensure the main thread exits when closing viewer during human action
        self.root = None
        self.action = None  # generate invalid action
        self.barrier.set()

    def close(self, event=None):
        """Close the GUI."""
        if self.root is not None:
            self.root.destroy()

    def set_status(self, new_status):
        """Set the first line of the status bar."""
        s = self.status_text = new_status
        if self.substatus_text:
            s += "\n" + self.substatus_text
        self.status["text"] = s

    def set_substatus(self, new_substatus):
        """Set the second line of the status bar."""
        self.substatus_text = new_substatus
        self.set_status(self.status_text)

    def update(self, board, step, action):
        self.board = board
        if self.root is not None:
            self.root.after_idle(self._update_gui, board, step, action)

    def clean_board(self):
        for i in range(self.board.rows):
            for j in range(self.board.columns):
                self.canvas.delete("height%d%d" % (i, j))
                for k in range(4):
                    for l in range(2):
                        self.canvas.delete(
                            "towers%d%d%d%d" % (i, j, k, l))

    def _update_gui(self, board, step, action, invert=False):
        i1, j1, i2, j2 = action
        if (i1 == 0 and i2 == 0 and j1 == 0 and j2 == 0):
            self.clean_board()
            for i in range(self.board.rows):
                for j in range(self.board.columns):
                    tower = board.get_tower(board.m[i][j])
                    height = board.get_height(board.m[i][j])
                    y = (i + .5) * self.w * self.ratio_yx + \
                    4 * self.dist_tokens
                    x = (j + .5) * self.w
                    for k in range(height):
                        for l in range(2):
                            half_token = tower[k][l]
                            if half_token == -1:
                                color = "red"
                            elif half_token == 1:
                                color = "yellow"
                            else:
                                color = "grey"
                            if (k == (height - 1) and l == 1):
                                o = self.canvas.create_oval(
                                    x - self.r_token_x,
                                    y - self.r_token_y,
                                    x + self.r_token_x,
                                    y + self.r_token_y,
                                    fill=color,
                                    tags=["towers%d%d%d%d" % (i, j, k, l)])
                            else:
                                self.canvas.create_oval(
                                    x - self.r_token_x,
                                    y - self.r_token_y,
                                    x + self.r_token_x,
                                    y + self.r_token_y,
                                    fill=color,
                                    tags=["towers%d%d%d%d" % (i, j, k, l)])
                            y -= self.dist_tokens
                    if height > 0:
                        self.canvas.create_text(x,
                                                y,
                                                text=str(height),
                                                font=self.font,
                                                tags=["height%d%d" % (i, j)])
                    self.tower_ids[i][j] = o
                    self._mark((i, j))  # ensure coherent unselected appearance
        else:
            if(invert and board.get_height(board.m[i1][j1]) != 0):
                height1 = board.get_height(board.m[i1][j1])
                height2 = board.get_height(board.m[i2][j2])
                formerHeight1 = height1 + height2
                y = (i2 - i1) * self.w * self.ratio_yx \
                + (self.dist_tokens * 2 * height1)
                x = (j2 - j1) * self.w
                self.tower_ids[i1][j1] = self.canvas.find_withtag(
                    "towers%d%d%d%d" % (i1, j1, height1 - 1, 1))
                for k in range(height1, formerHeight1):
                    for l in range(2):
                        self.canvas.move(
                            "towers%d%d%d%d" % (i1, j1, k, l), x, y)
                        self.canvas.addtag_withtag(
                            "towers%d%d%d%d" % (i2, j2, k - height1, l),
                            "towers%d%d%d%d" % (i1, j1, k, l))
                        self.canvas.dtag(
                            "towers%d%d%d%d" % (i2, j2, k - height1, l),
                            "towers%d%d%d%d" % (i1, j1, k, l))
                        if (k == (formerHeight1 - 1) and l == 1):
                            self.tower_ids[i2][j2] = \
                            self.canvas.find_withtag(
                                "towers%d%d%d%d" % (i2, j2, k - height1, l))
                        self.canvas.tag_raise(
                            "towers%d%d%d%d" % (i2, j2, k - height1, l))
                self.canvas.move(
                    "height%d%d" % (i1, j1), 0, self.dist_tokens * 2 * height2)
                self.canvas.itemconfigure("height%d%d" % (i1, j1),
                                          text=str(height1))
                self.canvas.tag_raise("height%d%d" % (i1, j1))
                self.canvas.create_text(
                    (j2 + .5) * self.w,
                    (i2 + .5) * self.w * self.ratio_yx +
                    self.dist_tokens * (4 - 2 * height2),
                    text=str(height2), font=self.font,
                    tags=["height%d%d" % (i2, j2)])
                self._mark((i1, j1))  # ensure coherent unselected appearance
                self._mark((i2, j2))  # ensure coherent unselected appearance
            else:
                self.canvas.delete("height%d%d" % (i1, j1))
                tower1Tags = []
                for k in range(4):
                    for l in range(2):
                        if self.canvas.find_withtag(
                            "towers%d%d%d%d" % (i1, j1, k, l)):
                            tower1Tags.append(
                                "towers%d%d%d%d" % (i1, j1, k, l))
                height1 = len(tower1Tags) // 2
                height2 = board.get_height(board.m[i2][j2])
                y = (i2 - i1) * self.w * self.ratio_yx - \
                (self.dist_tokens * 2 * (height2 - height1))
                x = (j2 - j1) * self.w
                if height1 == height2:
                    y += (height2 * 2 - 1) * self.dist_tokens
                    for k in range(height1 - 1, -1, -1):
                        for l in range(1, -1, -1):
                            self.canvas.move(
                                "towers%d%d%d%d" % (i1, j1, k, l), x, y)
                            self.canvas.addtag_withtag(
                                "towers%d%d%d%d" % (i2, j2,
                                                    height1 - k - 1, 1 - l),
                                "towers%d%d%d%d" % (i1, j1, k, l))
                            self.canvas.dtag(
                                "towers%d%d%d%d" % (i2, j2,
                                                    height1 - k - 1, 1 - l),
                                "towers%d%d%d%d" % (i1, j1, k, l))
                            if (k == 0 and l == 0):
                                self.tower_ids[i2][j2] = \
                                self.canvas.find_withtag(
                                    "towers%d%d%d%d" % (i2, j2,
                                                        height1 - k - 1,
                                                        1 - l))
                            self.canvas.tag_raise(
                                "towers%d%d%d%d" % (i2, j2,
                                                    height1 - k - 1, 1 - l))
                            y -= 2 * self.dist_tokens
                    self.canvas.create_text((j2 + .5) * self.w,
                                            (i2 + .5) * self.w *
                                            self.ratio_yx +
                                            self.dist_tokens *
                                            (4 - 2 * height2),
                                            text=str(height2),
                                            font=self.font,
                                            tags=["height%d%d" % (i2, j2)])
                    self._mark((i2, j2))
                else:
                    for k in range(height1):
                        for l in range(2):
                            self.canvas.move(
                                "towers%d%d%d%d" % (i1, j1, k, l), x, y)
                            self.canvas.addtag_withtag(
                                "towers%d%d%d%d" % (i2, j2,
                                                    k + (height2 - height1),
                                                    l),
                                "towers%d%d%d%d" % (i1, j1, k, l))
                            self.canvas.dtag(
                                "towers%d%d%d%d" % (i2, j2,
                                                    k + (height2 - height1),
                                                    l),
                                "towers%d%d%d%d" % (i1, j1, k, l))
                            if (k == (height1 - 1) and l == 1):
                                self.tower_ids[i2][j2] = \
                                self.canvas.find_withtag(
                                    "towers%d%d%d%d" % (i2, j2,
                                                        k +
                                                        (height2 - height1),
                                                        l))
                            self.canvas.tag_raise(
                                "towers%d%d%d%d" % (i2, j2,
                                                    k + (height2 - height1),
                                                    l))
                    if height2 > 0:
                        self.canvas.move("height%d%d" % (i2, j2),
                                         0,
                                         -height1 * 2 * self.dist_tokens)
                        self.canvas.itemconfigure("height%d%d" % (i2, j2),
                                                  text=str(height2))
                        self.canvas.tag_raise("height%d%d" % (i2, j2))
                    self._mark((i2, j2))
        if step % 2:
                player = "Red"
        else:
            player = "Yellow"
        self.set_status("Step %d: %s's turn." % (step, player))
        self.set_substatus("")

    def play(self, percepts, step, time_left):
        if self.root is None:
            return None
        if 1 - step % 2:
            self.player = "Red"
        else:
            self.player = "Yellow"
        self.barrier.clear()
        self.root.after_idle(self._play_start)
        self.barrier.wait()
        return self.action

    def _play_start(self):
        """Configure GUI to accept user input."""
        self.play_step = 1
        self.selection = None
        self.set_substatus("Select a tower to move.")
        self.canvas.bind("<Leave>", self._play_leave)
        self.canvas.bind("<Motion>", self._play_motion)
        self.canvas.bind("<Button-1>", self._play_click)

    def _play_leave(self, event):
        """Handler for Mouse Leave event"""
        if event.state & 0x100:  # leave event is also called on mouse click
            return
        if self.selection is not None:
            if self.play_step != 2 or self.selection != self.action:
                self._mark(self.selection)
            self.selection = None

    def _play_motion(self, event):
        """Handler for Mouse Motion event"""
        self._play_leave(event)
        i, j = int(event.y / (self.w * self.ratio_yx)), int(event.x / self.w)
        if i < 0 or i >= self.board.rows or j < 0 or j >= self.board.columns:
            return
        if (self.play_step == 1 and self.board.is_tower_movable(i, j)) or \
                (self.play_step == 2 and self.action == (i, j)):
            self.selection = (i, j)
            self._mark(self.selection, "origin")
        elif self.play_step == 2 and self.action + (i, j) in self.moves:
            self.selection = (i, j)
            self._mark(self.selection, "destination")

    def _play_click(self, event):
        """Handler for Mouse Click event"""
        if self.selection is None:
            return
        i, j = self.selection
        if self.play_step == 1:
            # Select origin tower
            self._mark(self.selection, "origin")
            self.action = self.selection
            self.moves = list(self.board.get_tower_actions(i, j))
            self.play_step = 2
            self.set_substatus(
                "Select a tower to gobble or a returning case to move to.")
        elif self.play_step == 2 and self.selection == self.action:
            # Deselect origin tower
            self._play_start()
        elif self.play_step == 2:
            # Select destination tower
            action = self.action + (i, j)
            if action in self.moves:
                self._mark(self.action)
                self._mark(self.selection)
                self.action += self.selection
                self.set_substatus("")
                self.canvas.unbind("<Leave>")
                self.canvas.unbind("<Motion>")
                self.canvas.unbind("<Button-1>")
                self.barrier.set()

    def _mark(self, position, style="unselected"):
        """Mark tower as unselected, origin or destination."""
        i, j = position
        if self.board.get_height(self.board.m[i][j]) > 0:
            o = self.tower_ids[i][j]
        else:
            o = self.cell_ids[i][j]
        if isinstance(o, list):
            raise TypeError("A single int was expected")
        if style == "unselected":
            if self.board.get_height(self.board.m[i][j]) > 0:
                self.canvas.itemconfigure(o, outline="black", width=1)
            else:
                self.canvas.itemconfigure(o, outline="black", width=0)
        elif style == "origin":
            self.canvas.itemconfigure(o, outline="darkgreen", width=3)
        elif style == "destination":
            self.canvas.itemconfigure(o, outline="blue", width=3)
        else:
            assert False

    def finished(self, board, steps, score, reason=""):
        if self.root is None:
            return
        if score == 0:
            s = "Draw game"
        elif score < 0:
            s = "Red has won"
        else:
            s = "Yellow has won"
        s += " after " + str(steps) + " steps."
        self.root.after_idle(self.set_status, s)
        if reason:
            self.root.after_idle(self.set_substatus, reason)

    def replay(self, trace, show_end=False):
        """Replay a game given its saved trace.

        Attributes:
        trace -- trace of the game
        show_end -- start with the final state instead of the initial state

        """
        self.trace = trace
        # generate all boards to access them backwards
        self.boards = [trace.get_initial_board()]
        self.actions = [(0, 0, 0, 0)]
        for action, t in trace.actions:
            self.actions.append(action)
            b = self.boards[-1].clone()
            b.play_action(action)
            self.boards.append(b)
        if self.root is not None:
            self.root.after_idle(self._replay_gui, show_end)
        self.run()

    def _replay_gui(self, show_end):
        """Initialize replay UI"""
        self.b_next = Button(self.root, text=">", command=self._replay_next)
        self.b_play = Button(self.root, text="Play", command=self._replay_play)
        self.b_prev = Button(self.root, text="<", command=self._replay_prev)
        self.b_next.pack(side=RIGHT)
        self.b_play.pack(side=RIGHT)
        self.b_prev.pack(side=RIGHT)
        self.root.bind_all("<Left>", self._replay_prev)
        self.root.bind_all("<Right>", self._replay_next)
        self.root.bind_all("<Home>", self._replay_first)
        self.root.bind_all("<End>", self._replay_last)
        self.root.bind_all("<space>", self._replay_play)
        self.playing = False
        if show_end:
            self._replay_goto(len(self.boards) - 1, False)
        else:
            self._replay_goto(0, False)

    def _replay_goto(self, step, invert=False):
        """Update UI to show step step."""
        self.step = step
        if invert:
            self._update_gui(self.boards[step], step,
                             (self.actions[step + 1][2],
                              self.actions[step + 1][3],
                              self.actions[step + 1][0],
                              self.actions[step + 1][1]), invert)
        else:
            self._update_gui(self.boards[step], step, self.actions[step])
        if step == len(self.boards) - 1:
            self.finished(self.boards[step], step, self.trace.score,
                          self.trace.reason)
            if self.playing:
                self.playing = False
                self.b_play["text"] = "Play"
        if self.playing:
            self.after_id = self.root.after(
                    int(self.trace.actions[step][1] * 1000),
                    self._replay_goto, step + 1, False)
        else:
            if step == 0:
                self.b_prev["state"] = DISABLED
            else:
                self.b_prev["state"] = NORMAL
            if step == len(self.boards) - 1:
                self.b_next["state"] = DISABLED
            else:
                self.b_next["state"] = NORMAL

    def _replay_next(self, event=None):
        if not self.playing and self.step < len(self.boards) - 1:
            self._replay_goto(self.step + 1, False)

    def _replay_prev(self, event=None):
        if not self.playing and self.step > 0:
            self._replay_goto(self.step - 1, True)

    def _replay_first(self, event=None):
        if not self.playing:
            self._replay_goto(0, False)

    def _replay_last(self, event=None):
        if not self.playing:
            self._replay_goto(len(self.boards) - 1, False)

    def _replay_play(self, event=None):
        if self.playing:
            self.root.after_cancel(self.after_id)
            self.playing = False
            self.b_play["text"] = "Play"
            self._replay_goto(self.step, False)
        else:
            self.playing = True
            self.b_prev["state"] = DISABLED
            self.b_next["state"] = DISABLED
            self.b_play["text"] = "Pause"
            if self.step < len(self.boards) - 1:
                self._replay_goto(self.step, False)
            else:
                self._replay_goto(0, False)
