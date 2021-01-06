import goal
import block
import player
import blocky
import game
import random
from settings import COLOUR_LIST

board = block.Block((0, 0), 750, random.choice(COLOUR_LIST), 0, 3)
copy = board.create_copy()
copy_cat = board
assert id(board) != id(copy)
assert board == copy
flat_b = goal._flatten(board)
flat_c = goal._flatten(copy)
for i in range(len(flat_b)):
    for j in range(len(flat_c)):
        assert flat_b[i][j] == flat_c[i][j]


def test_player() -> None:
    players = player.SmartPlayer(1, goal.PerimeterGoal((234, 62, 112)), 5)
    move = players.generate_move(board)
    possible_moves = players.list_of_moves
    for moves in possible_moves:
        print('hello')
