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
    # A list of all mills in the game (plz someone check i definitely couldve missed some)
    MILL_LIST = [
        ("a1", "a4", "a7"),
        ("a7", "d7", "g7"),
        ("g7", "g4", "g1"),
        ("a1", "d1", "g1"),
        ("b2", "d2", "f2"),
        ("b2", "b4", "b6"),
        ("b6", "d6", "f6"),
        ("f6", "f4", "f2"),
        ("a4", "b4", "c4"),
        ("e4", "f4", "g4"),
        ("d1", "d2", "d3"),
        ("d5", "d6", "d7"),
        ("c3", "d3", "e3"),
        ("c3", "c4", "c5"),
        ("c5", "d5", "e5"),
        ("e5", "e4", "e3")
    ]
    def __init__(self):
        # Board positions
        self.positions = ["a1", "a4", "a7", "b2", "b4", "b6",
                          "c3", "c4", "c5", "d1", "d2", "d3",
                          "d5", "d6", "d7", "e3", "e4", "e5",
                          "f2", "f4", "f6", "g1", "g4", "g7"]
        
        # Initialize the board
        board = {pos: None for pos in self.positions}

        # All positions are initially available for placement
        moves = self.positions.copy()

        self.initial = GameState(to_move='X', utility=0, board=board, moves=moves)

    def actions(self, state):
        """Return a list of the legal moves at this point."""
        return [pos for pos in state.board if state.board[pos] is None]

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        # Make sure the move is valid
        if move not in state.board or state.board[move] is not None:
            return "INVALID"
        
        # Create a new board with the new move
        new_board = state.board.copy()
        new_board[move] = state.to_move

        # Remove the move from the list of available moves
        new_moves = [m for m in state.moves if m != move]

        # Switch to the other player
        next_player = 'O' if state.to_move == 'X' else 'X'

        return GameState(to_move=next_player, utility=0, board=new_board, moves=new_moves)

    def utility(self, state, player):
        """Return the value of this final state to player."""
        # TODO: add in logic to check other winning/losing conditions other than mills and pieces

        opponent = 'O' if player == 'X' else 'X'

        # Count the number of mills for each player
        mills_player = 0
        mills_opponent = 0
        for mill in Lasker_Morris.MILL_LIST:
            if all(state.board[pos] == player for pos in mill):
                mills_player += 1
            elif all(state.board[pos] == opponent for pos in mill):
                mills_opponent += 1

        # Count the number of pieces for each player
        pieces_player = sum(1 for pos in state.board if state.board[pos] == player)
        pieces_opponent = sum(1 for pos in state.board if state.board[pos] == opponent)

        # Combine the values into a single score, weights can change depending on testing and such
        score = 3 * (mills_player - mills_opponent) + (pieces_player - pieces_opponent)

        # If the game is over, return a high or low value
        if self.terminal_test(state):
            if self.check_win(state, player):
                return 100
            elif self.check_win(state, opponent):
                return -100

        return score
    
    def check_mill(self, board, pos, player):
        """
        Check if the move at a given position forms a mill for the player
        """
        mills_formed = []
        for mill in Lasker_Morris.MILL_LIST:
            if pos in mill and all(board[p] == player for p in mill):
                mills_formed.append(mill)
        return mills_formed

    def check_win(self, state, player):
        """
        Check if a player has won the game
        """
        return NotImplementedError

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

def main():
    # Read initial color/symbol
    player_id = input().strip()
    first_move_made = 0
    tic = Lasker_Morris()
    tac = tic.initial #gamestate
    while True:
        # first move logic
        if player_id == "blue" and first_move_made == 0:
            moveX1 = (alpha_beta_search(tac, tic)) #get best 1st move as X
            # update internal board with our move
            tac = Lasker_Morris.result(tic, tac, moveX1)
            first_move_made = first_move_made + 1
            print(moveX1, flush=True) #send move to referee

        try:
            if player_id == "orange":
                # Read opponent's move
                opponent_inputX = input().strip() #opponent move as X
                if #some valid move check on op input == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                # update internal board with opponent move
                tac = Lasker_Morris.result(tic, tac, opponent_inputX)
                if tac == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                moveO1 = alpha_beta_search(tac, tic) #get best move as O
                tac = Lasker_Morris.result(tic, tac, moveO1)
                print(moveO1, flush=True)
                #check for orange win and terminate if win is found
                if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 100:
                    print("GAME OVER: orange player wins!")
                    sys.exit(0)


            # Read opponent's move
            opponent_inputO = input().strip() #opponent move as O
            if #some valid move check on op input == "INVALID":
                print("orange player has played an invalid move; blue player wins!", flush=True)
                sys.exit(0)
            # update internal board with opponent move
            tac = Lasker_Morris.result(tic, tac, translated_op_inputO)
            if tac == "INVALID":
                print("orange player has played an invalid move; blue player wins!", flush=True)
            # Your move logic here
            moveX2 = alpha_beta_search(tac, tic)  # get best move as X
            tac = Lasker_Morris.result(tic, tac, moveX2)
            # Send move to referee
            print(moveX2, flush=True)
            # check for blue win and terminate if win is found
            if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 100:
                print("GAME OVER: blue player wins!")
                sys.exit(0)

            #need utility value for draws/check for draws
            if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 0:
                print("GAME OVER: it's a draw!")
                sys.exit(0)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
