"""
Tic Tac Toe Player
"""

import math

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
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check horizontal wins
    result = ""
    for row in board: 
        for item in row: 
            result += item

        if X*NUM_MATCH in result: 
            return X
        elif O*NUM_MATCH in result: 
            return O
        result = ""

    # check vertical
    result = ""
    for col in range(len(board[0])): 
        for row in range(len(board)): 
            result += board[row][col]

        if X*NUM_MATCH in result: 
            return X
        elif O*NUM_MATCH in result: 
            return O
        result = ""


    # check diagonal \
    result = ""
    for i in range(len(board)):
        result += board[i][i]
        
    if X*NUM_MATCH in result: 
        return X
    elif O*NUM_MATCH in result: 
        return O
    result = ""

    # check diagonal /
    result = ""
    for i in range(len(board)-1, -1, -1):
        result += board[NUM_MATCH-i-1][i]
        
    if X*NUM_MATCH in result: 
        return X
    elif O*NUM_MATCH in result: 
        return O
    result = ""

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
    winner = winner(board)
    if winner == X: 
        return 1
    elif winner == O: 
        return -1 
    else: 
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError

print(terminal([[X, EMPTY, X],
            [O, EMPTY, X],
            [X, EMPTY, O]]))