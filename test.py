from super_player import *

import unittest

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        State.setup()

    def code2color(self, code):
        if code == " ":
            return 42
        elif code == "Y":
            return 1
        elif code == "R":
            return -1
        else:
            return 0

    def parse(self, state):
        s = list(range(36))
        for i, line in enumerate(state.strip().splitlines()):
            for j, c in enumerate(line.split()):
                h = int(c[0])
                if h:
                    bot = self.code2color(c[1])
                    top = self.code2color(c[2])
                    s[i*6+j] = (h, bot, top)
                else:
                    s[i*6+j] = EMPTY_PILE
        return s

    def test_eval(self):
        state = """
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), 0)

        state = """
        4NY 0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), 4*SURE_THING)

        state = """
        4NR 0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), -4*SURE_THING)

        state = """
        0   4NY 0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), 0)

        state = """
        0   4YN 0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), 4*SURE_THING)

        state = """
        3NY 0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        self.assertEqual(State.score(self.parse(state)), 3*SURE_THING)

        state = """
        3YN 0   4NR 0   2NN 0
        0   2YN 0   0   0   4YN
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        0   0   0   0   0   0
        """
        s = 0 - 4*SURE_THING + 0 \
          + 0 + 0
        self.assertEqual(State.score(self.parse(state)), s)

        state="""
        3YN 0   4NR 0   2NN 0
        0   2YN 0   0   0   4YN
        2NN 0   1NR 0   4RN 0
        0   0   0   0   0   2NR
        0   0   0   0   4NR 0
        0   4YY 1NN 1NR 2NR 0
        """
        s = 0 - 4*SURE_THING + 0 \
          + 0 + 0 \
          + 0 - 1*SURE_THING + 0 \
          - 2*SURE_THING \
          - 4*SURE_THING \
          + 4*SURE_THING - MAYBE - LOST
        self.assertEqual(State.score(self.parse(state)), s)

if __name__ == '__main__':
    unittest.main()
