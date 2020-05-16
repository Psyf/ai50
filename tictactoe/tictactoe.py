"""
Tic Tac Toe Player
"""

import math
import random

X = "X"
O = "O"
EMPTY = ""
NUM_MATCH = 3


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    x_count = 0
    o_count = 0

    for row in board: 
        for mark in row: 
            if mark == X: 
                x_count += 1
            elif mark == O: 
                o_count += 1

    if (x_count+o_count)%2: 
        return O 
    else: 
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    tmp_res = []
    for i in range(len(board)): 
        for j in range(len(board[0])): 
            if board[i][j] == EMPTY: 
                tmp_res.append((i, j))
    
    return tmp_res


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    copy_of_board = []
    for i in range(len(board)): 
        copy_of_board.append([])
        for j in range(len(board[0])): 
            copy_of_board[i].append(board[i][j])

    if action not in actions(board): 
        raise Exception("Illegal Move!")
    else: 
        copy_of_board[action[0]][action[1]] = player(board)
    
    return copy_of_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check horizontal wins
    tmp_res = ""
    for row in board: 
        for item in row: 
            tmp_res += item

        if X*NUM_MATCH in tmp_res:
            return X
        elif O*NUM_MATCH in tmp_res:
            return O
        tmp_res = ""

    # check vertical
    tmp_res = ""
    for col in range(len(board[0])): 
        for row in range(len(board)): 
            tmp_res += board[row][col]

        if X*NUM_MATCH in tmp_res:
            return X
        elif O*NUM_MATCH in tmp_res:
            return O
        tmp_res = ""

    # check diagonal \
    tmp_res = ""
    for i in range(len(board)):
        tmp_res += board[i][i]
        
    if X*NUM_MATCH in tmp_res:
        return X
    elif O*NUM_MATCH in tmp_res:
        return O

    # check diagonal /
    tmp_res = ""
    for i in range(len(board)-1, -1, -1):
        tmp_res += board[NUM_MATCH-i-1][i]
        
    if X*NUM_MATCH in tmp_res:
        return X
    elif O*NUM_MATCH in tmp_res:
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    
    if winner(board) is not None: 
        return True
    else: 
        for row in board: 
            for item in row: 
                if item is EMPTY: 
                    return False 
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    tmp_res = winner(board)
    if tmp_res == X:
        return 1
    elif tmp_res == O:
        return -1 
    else: 
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        return maximizer(board)[1]
    elif player(board) == O:
        return minimizer(board)[1]


def maximizer(board):
    possible_actions = actions(board)
    
    if len(possible_actions) == 1:
        return utility(result(board, possible_actions[0])), possible_actions[0]
    else: 
        best_case = (float("-inf"), (None, None))
        for action in possible_actions:
            tmp_res = minimizer(result(board, action))
            if tmp_res[0] > best_case[0]:
                best_case = tmp_res[0], action

        return best_case


def minimizer(board):
    possible_actions = actions(board)

    if len(possible_actions) == 1:
        return utility(result(board, possible_actions[0])), possible_actions[0]
    else:
        best_case = (float("inf"), (None, None))
        for action in possible_actions:
            tmp_res = maximizer(result(board, action))
            if tmp_res[0] < best_case[0]:
                best_case = tmp_res[0], action

        return best_case
