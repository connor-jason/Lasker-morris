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


Class Lasker_Morris(Game):
#Empty for now



def main():
    # Read initial color/symbol
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
