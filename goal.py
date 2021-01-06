"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    type_of_goal = random.randint(1, 2)
    lst = []
    colours = COLOUR_LIST[:]
    if type_of_goal == 1:
        for _ in range(num_goals):
            num = random.randint(0, len(colours)-1)
            colour = colours[num]
            goal = PerimeterGoal(colour)
            colours.remove(colour)
            lst.append(goal)
    else:
        for _ in range(num_goals):
            num = random.randint(0, len(colours)-1)
            colour = colours[num]
            goal = BlobGoal(colour)
            colours.remove(colour)
            lst.append(goal)
    return lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if not block.children and block.level == block.max_depth:
        return [[block.colour]]
    elif not block.children:
        outer_list = []
        count_goal = 2**(block.max_depth - block.level)
        for _ in range(count_goal):
            inner_list = []
            for __ in range(count_goal):
                inner_list.append(block.colour)
            outer_list.append(inner_list)
        return outer_list
    else:
        upper_left_list = _flatten(block.children[1])
        lower_left_list = _flatten(block.children[2])
        upper_right_list = _flatten(block.children[0])
        lower_right_list = _flatten(block.children[3])
        outer_list = []
        for j in range(len(upper_left_list)):
            inner_list = []
            inner_list.extend(upper_left_list[j])
            inner_list.extend(lower_left_list[j])
            outer_list.append(inner_list)
        for j in range(len(upper_right_list)):
            inner_list = []
            inner_list.extend(upper_right_list[j])
            inner_list.extend(lower_right_list[j])
            outer_list.append(inner_list)
        return outer_list


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal where the player's score is counter by the number of target blocks
    on the perimeter of the board
    """
    def score(self, board: Block) -> int:
        """Generates the score for this <board> based on self and returns the
        score
        """
        final_score = 0
        flat = _flatten(board)
        length = len(flat)
        for i in range(length):
            if flat[0][i] == self.colour:
                final_score += 1
            if flat[i][0] == self.colour:
                final_score += 1
            if flat[length - 1][i] == self.colour:
                final_score += 1
            if flat[i][length - 1] == self.colour:
                final_score += 1
        return final_score

    def description(self) -> str:
        """Returns a description of this goal
        """
        colours = {}
        for colour in COLOUR_LIST:
            colours[colour] = colour_name(colour)
        string = f'PerimeterGoal: Target colour = {colours[self.colour]}'
        return string


class BlobGoal(Goal):
    """A goal where the player's score is counted by the number of target blocks
    that are connected
    """
    def score(self, board: Block) -> int:
        """Generates the score for this <board> based on self and returns the
        score
        """
        final_score = []
        flat = _flatten(board)
        size_of_board = len(flat)
        appearance = []
        columns = []

        for _ in range(size_of_board):
            columns.append(-1)
        for _ in range(size_of_board):
            appearance.append(columns.copy())

        for j in range(size_of_board):
            for k in range(size_of_board):
                if appearance[j][k] == -1:
                    final_score.append(self._undiscovered_blob_size((j, k),
                                                                    flat,
                                                                    appearance))
        return max(final_score)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if (pos[1] < 0 or pos[1] >= len(board[0])) or (pos[0] < 0
                                                       or pos[0] >= len(board)):
            return 0
        elif visited[pos[0]][pos[1]] == 0 or visited[pos[0]][pos[1]] == 1:
            return 0
        elif board[pos[0]][pos[1]] != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0
        else:
            visited[pos[0]][pos[1]] = 1
            start = self._undiscovered_blob_size((pos[0], pos[1] + 1), board,
                                                 visited) + \
                self._undiscovered_blob_size((pos[0], pos[1] - 1), board,
                                             visited) + \
                self._undiscovered_blob_size((pos[0] + 1, pos[1]), board,
                                             visited) + \
                self._undiscovered_blob_size((pos[0] - 1, pos[1]), board,
                                             visited) + 1
            return start

    def description(self) -> str:
        """Returns a description of this goal
        """
        colours = {}
        for colour in COLOUR_LIST:
            colours[colour] = colour_name(colour)
        string = f'BlobGoal: Target colour = {colours[self.colour]}'
        return string


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
