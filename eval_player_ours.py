'''Benoit Daloze & Xavier de Ryckel'''

from sarena import *
import minimax

# score
SURE_THING = 10
BACKSTAB = 4
MAYBE = 2

class EvalPlayerOurs(Player, minimax.Game):
    def successors(self, board):
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            yield action, new_board

    def cutoff(self, board, depth):
        return depth == 1

    def convert_color_to_score(color):
        if color == -1:
            return -1
        elif color == 1:
            return 1
        else:
            return 0

    def score_at(board, i, j, tower):
        arrows = (tower[0] == 4)
        height = board.get_height(tower)
        if height == 0:
            return 0

        bot = EvalPlayerOurs.convert_color_to_score(board.get_tower(tower)[0][0])
        top = EvalPlayerOurs.convert_color_to_score(board.get_tower(tower)[-1][-1])
        if arrows: # on arrows
            if height == 4:
                # for any 4-tower, top color wins
                return SURE_THING * 4 * top
            else:
                no_neighbors = True
                for y, x in ((i-1, j), (i, j+1), (i+1, j), (i, j-1)):
                    if 0 <= x < board.columns and 0 <= y < board.rows:
                        n = board.get_height(board.m[y][x])
                        if n != 0:
                            no_neighbors = False
                            break
                if no_neighbors:
                    # for any tower with no neighbors, top color wins
                    return SURE_THING * height * top
                else: # height is 1-3, some neighbors
                    # bot is useless
                    # top can go over another pile
                    return MAYBE * top # * height ?
        else: # on normal
            if height == 4:
                # for any 4-tower, bottom color wins (except if all neighbors around until EOG)
                return SURE_THING * 4 * bot
            else: # height is 1-3
                # (for any tower with no neighbors in range 2, bottom color wins => too rare)
                # bot will be ~ likely returned and win a tower
                return BACKSTAB * bot

    def evaluate(self, board):
        score = 0
        for i, j, tower in board.get_towers():
            score += EvalPlayerOurs.score_at(board, i, j, tower)
        return score

    def play(self, percepts, step, time_left):
        # We are always the yellow player
        board = Board(percepts)
        return minimax.search(board, self)

if __name__ == "__main__":
    player = EvalPlayerOurs()
    player_main(player)
