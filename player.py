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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    num_players = num_human + num_random + len(smart_players)
    goals = generate_goals(num_players)
    players = []
    for i in range(num_human):
        players.append(HumanPlayer(i, goals.pop()))
    counter = num_human
    for _ in range(num_random):
        players.append(RandomPlayer(counter, goals.pop()))
        counter += 1
    for player in smart_players:
        players.append(SmartPlayer(counter, goals.pop(), player))
        counter += 1
    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    x_co, y_co = block.position
    size = block.size
    is_in_block = False
    if block.level > level:
        return None
    if x_co <= location[0] < x_co + size and y_co <= location[1] < y_co + size:
        is_in_block = True
    if is_in_block and level > block.level and block.children is not None:
        for child in block.children:
            if _get_block(child, location, level) is not None:
                return _get_block(child, location, level)
    if is_in_block:
        return block
    return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError

    def _create_valid_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Generates a random valid move on <board> and returns it"""
        is_valid = False

        possible_moves = {ROTATE_CLOCKWISE: ('rotate', 1),
                          ROTATE_COUNTER_CLOCKWISE: ('rotate', 3),
                          SWAP_HORIZONTAL: ('swap', 0),
                          SWAP_VERTICAL: ('swap', 1), SMASH: ('smash', None),
                          COMBINE: ('combine', None), PAINT: ('paint', None)}
        block_to_move = 0
        move = ('swap', 1)
        while not is_valid:
            random_level = random.randint(0, board.max_depth)
            counter = 0
            block_to_move = board.create_copy()
            has_kids = True
            if not block_to_move.children:
                has_kids = False
            while counter < random_level and has_kids:
                block_to_move = block_to_move.children[random.randint(0, 3)]
                if not block_to_move.children:
                    has_kids = False
                counter += 1
            num = random.randint(0, len(possible_moves) - 1)
            if num == 0:
                move = possible_moves[ROTATE_CLOCKWISE]
            elif num == 1:
                move = possible_moves[ROTATE_COUNTER_CLOCKWISE]
            elif num == 2:
                move = possible_moves[SWAP_VERTICAL]
            elif num == 3:
                move = possible_moves[SWAP_HORIZONTAL]
            elif num == 4:
                move = possible_moves[SMASH]
            elif num == 5:
                move = possible_moves[COMBINE]
            else:
                move = possible_moves[PAINT]
            if move == possible_moves[ROTATE_CLOCKWISE] \
                    and block_to_move.rotate(move[0]) is True:
                is_valid = True
            elif move == possible_moves[ROTATE_COUNTER_CLOCKWISE] \
                    and block_to_move.rotate((move[1])) is True:
                is_valid = True
            elif move == possible_moves[SWAP_HORIZONTAL] \
                    and block_to_move.swap(0):
                is_valid = True
            elif move == possible_moves[SWAP_VERTICAL] \
                    and block_to_move.swap(1):
                is_valid = True
            elif move == possible_moves[SMASH] and block_to_move.smash():
                is_valid = True
            elif move == possible_moves[COMBINE] and block_to_move.combine():
                is_valid = True
            elif move == possible_moves[PAINT] and block_to_move.paint(
                    self.goal.colour):
                is_valid = True
        block_to_moved = _get_block(board, block_to_move.position,
                                    block_to_move.level)
        return move[0], move[1], block_to_moved


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """Takes the given <action> and the <block> it will be performed on and
    returns them all together as a tuple
    """
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    id: int
    goal: Goal
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, min(self._level, board.max_depth))

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A player that chooses a random valid move every turn
    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    id: int
    goal: Goal
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Doesn't use board, just returns None
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Determines whether the player is making a move or not
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None

        self._proceed = False
        return self._create_valid_move(board)


class SmartPlayer(Player):
    """This player generates a certain number of random moves (the amount
    depends on the difficulty) and chooses the one with the best outcome for the
    score

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _difficulty:
    #   The number of potential moves the player will look through to find the
    #   best from
    id: int
    goal: Goal
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Doesn't use board, just returns None
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Determines whether the player is making a move or not
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None
        current_score = self.goal.score(board)
        move_to_do = PASS[0], PASS[1], board
        counter = 0
        while counter < self._difficulty:
            copy = board.create_copy()
            move = self._create_valid_move(copy)
            potential_score = self._check_possible_score(copy, move)
            if potential_score > \
                    current_score:
                move_to_do = move
                current_score = potential_score
            counter += 1
        self._proceed = False
        if move_to_do != (PASS[0], PASS[1], board):
            block_to_move = _get_block(board, move_to_do[2].position,
                                       move_to_do[2].level)
            return move_to_do[0], move_to_do[1], block_to_move
        return move_to_do

    def _check_possible_score(self, copy: Block,
                              move: Tuple[str, Optional[int], Block]) -> int:
        """Performs <move> on a copy of <board> and returns the score of
        that move"""
        if (move[0], move[1]) in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
            move[2].rotate(move[1])
        elif (move[0], move[1]) in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
            move[2].swap(move[1])
        elif (move[0], move[1]) == SMASH:
            move[2].smash()
        elif (move[0], move[1]) == PAINT:
            move[2].paint(self.goal.colour)
        elif (move[0], move[1]) == COMBINE:
            move[2].combine()
        value = self.goal.score(copy)
        return value


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
