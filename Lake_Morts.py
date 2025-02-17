import math
import sys
from collections import namedtuple

#Code from Textbook with some minor modifications
GameState = namedtuple('GameState', 'to_move, utility, board, moves')

class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the legal moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


class Lasker_Morris(Game):
    # using blue and orange for players

    # i think rather than like TTT where the board just holds all moves
    # we could have it be ("pos#", "blue/orange")
    # when we change game board, if the move is a change + not from hand
    # we update the board by taking out the old move and putting in new move

    # we'll have to keep track of one's removed stones
    # (# of stones in hand is = init # - (board stones + removed stones)

    def __init__(self):
        entireBoard = ["a1", "a4", "a7", "b2", "b4", "b6", "c3", "c4", "c5", "d1", "d2", "d3", "d5", 
                "d6", "d7", "e3", "e4", "e5", "f2", "f4", "f6", "g1", "g4", "g7"]
        moves = [(x, y) for x in entireBoard
                for y in ['blue', 'orange']]
        # this makes a list of possible moves being the entire board with blue/orange
        self.initial = GameState(to_move='blue', utility=0, board={}, moves=moves)

    def actions(self, state):
        """Return a list of the legal moves at this point."""
        # need to have # of removed stones
        # get # of stones in hand
        # get # of stones on board - if this is less than 3, have bool
        # for each stone on board, get adjacent stones that are 
        # check if any created mill- if so, add those as well
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)















def alpha_beta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value_ab(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -math.inf
        for a in game.actions(state):
            v = max(v, min_value_ab(game.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value_ab(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = math.inf
        for a in game.actions(state):
            v = min(v, max_value_ab(game.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_search:
    best_score = -math.inf
    beta = math.inf
    best_action = None
    for a in game.actions(state):
        v = min_value_ab(game.result(state, a), best_score, beta)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action

#helper functions to translate between notations
def tuple_translate(tuple):
    if tuple[0] == 1:
        return 'a' + str(tuple[1])
    if tuple[0] == 2:
        return 'b' + str(tuple[1])
    if tuple[0] == 3:
        return 'c' + str(tuple[1])


def string_translate(string):
    if len(string) == 2:
        if string[0] == 'a':
            return (1, int(string[1]))
        if string[0] == 'b':
            return (2, int(string[1]))
        if string[0] == 'c':
            return (3, int(string[1]))
    else:
        return 'INVALID'










def main():
    # Read initial color/symbol
    # for Lasker Morris, this is blue or orange
    player_id = input().strip()
    first_move_made = 0
    tic = TicTacToe(3, 3, 3)
    tac = tic.initial #gamestate
    while True:
        # first move logic
        if player_id == "blue" and first_move_made == 0:
            moveX1 = (alpha_beta_search(tac, tic)) #get best 1st move as X
            # update internal board with our move
            tac = TicTacToe.result(tic, tac, moveX1)
            first_move_made = first_move_made + 1
            print(tuple_translate(moveX1), flush=True) #send move to referee

        try:
            if player_id == "orange":
                # Read opponent's move
                opponent_inputX = input().strip() #opponent move as X
                translated_op_inputX = string_translate(opponent_inputX)
                if translated_op_inputX == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                # update internal board with opponent move
                tac = TicTacToe.result(tic, tac, translated_op_inputX)
                if tac == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                moveO1 = alpha_beta_search(tac, tic) #get best move as O
                tac = TicTacToe.result(tic, tac, moveO1)
                print(tuple_translate(moveO1), flush=True)
                #check for orange win and terminate if win is found
                if TicTacToe.terminal_test(tic, tac) and tac.utility == 1:
                    print("GAME OVER: orange player wins!")
                    sys.exit(0)


            # Read opponent's move
            opponent_inputO = input().strip() #opponent move as O
            translated_op_inputO = string_translate(opponent_inputO)
            if translated_op_inputO == "INVALID":
                print("orange player has played an invalid move; blue player wins!", flush=True)
                sys.exit(0)
            # update internal board with opponent move
            tac = TicTacToe.result(tic, tac, translated_op_inputO)
            if tac == "INVALID":
                print("orange player has played an invalid move; blue player wins!", flush=True)
            # Your move logic here
            moveX2 = alpha_beta_search(tac, tic)  # get best move as X
            tac = TicTacToe.result(tic, tac, moveX2)
            # Send move to referee
            print(tuple_translate(moveX2), flush=True)
            # check for blue win and terminate if win is found
            if TicTacToe.terminal_test(tic, tac) and tac.utility == 1:
                print("GAME OVER: blue player wins!")
                sys.exit(0)

            if TicTacToe.terminal_test(tic, tac) and tac.utility == 0:
                print("GAME OVER: it's a draw!")
                sys.exit(0)
