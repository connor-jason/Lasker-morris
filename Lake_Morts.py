import math
import sys
from collections import namedtuple

#Code from Textbook with some minor modifications
GameState = namedtuple('GameState', 'to_move, utility, board, moves')

# Assumptions made:
# When a mill is created, opponent's piece *must* be removed


class Lasker_Morris():
    # A list of all mills in the game (plz someone check i definitely couldve missed some)
    # I believe this is good
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

        # All positions are initially available for placement by both players- only from hand, and no mills
        # This is in the form of 'h1/h2 a4 r0'
        moves = [f"{x} {y} {z}" for x in ['h1', 'h2'] 
                for y in self.positions 
                for z in ['r0']]

        self.initial = GameState(to_move='blue', utility=0, board=board, moves=moves)

    def actions(self, state, stonesRemoved):
        """Return a list of the legal moves at this point."""
        # This list will be in ['h1 a4 r0', 'd1 a4 e5'] etc format
        listOfMoves = []
        # This will depend on a lot of factors:
        # Current player- blue or orange
        curPlayer = state.to_move

        # Current players # of stones in hand, on board, removed
        boardStones = 0
        for x, y in state.board.items():
            if y == curPlayer:
                boardStones += 1
        # Unsure how to keep track of # of stones removed? For now, it will be passed as arg
        stonesRemoved = stonesRemoved
        handStones = 10 - (boardStones + stonesRemoved)

        # If number of stones to play is <=2, other player wins, so return no moves
        if (handStones == 0 and boardStones <= 2):
            return listOfMoves

        # Empty squares on board
        emptySquares = []
        for x, y in state.board.items():
            if y == None:
                emptySquares.append(x)
        
        # Create moves here:
        # If hand > 0, for each empty square:
        # Add it to moves 'h1/h2 square r0' (and also check for mills)
        if (handStones > 0):
            hand = 'h2'
            if curPlayer == 'blue':
                hand = 'h1'
            for sq in emptySquares:
                milledMoves = self.getMillMoves(state, hand, sq, curPlayer)
                # if no mill is created:
                if milledMoves == None:
                    listOfMoves.append(f'{hand} {sq} r0')
                else:
                    for move in milledMoves:
                        listOfMoves.append(move)
                
        # If boardStones > 3
        # For each current square, check all adjacent squares
        # Only add move if the adj square is empty
        # need to check for mills though also
        pSquares = []
        for x, y in state.board.items():
            if y == curPlayer:
                pSquares.append(x)
        if boardStones > 3:
            for sq in pSquares:
                # helper to return all adj sq's
                # then, remove all adjs that are NOT empty
                allAdjs = self.adj(sq)
                adjSqs = []
                for x in allAdjs:
                    if state.board[x] is None:
                        adjSqs.append(x)
                for adj in adjSqs:
                    millMoves = self.getMillMoves(state, adj, sq, curPlayer)
                    if millMoves == None:
                        listOfMoves.append(f'{adj} {sq} r0')
                    else:
                        for move in millMoves:
                            listOfMoves.append(move)


        # If hand == 0, boardStones == 3: pieces can fly
        # Thus, add all emptySquares 'd1 square r0' (and also check for mills)
        if (handStones == 0 and boardStones == 3):
            for sq in pSquares:
                for empty in emptySquares:
                    millMoves = self.getMillMoves(state, empty, sq, curPlayer)
                    if millMoves == None:
                        listOfMoves.append(f'{empty} {sq} r0')
                    else:
                        for move in millMoves:
                            listOfMoves.append(move)

        # This is designed to be exhaustive - send back every single specific valid move
        return listOfMoves

    def adj(self, pos):
        # helper function to return all adjacent sqs to sq
        if pos == 'a1':
            return ['a4', 'd1']
        elif pos == 'a4':
            return ['a1', 'a7', 'b4']
        elif pos =='a7':
            return ['a4', 'd7']
        elif pos == 'b2':
            return ['b4', 'd2']
        elif pos == 'b4':
            return ['a4', 'b2', 'b6', 'c4']
        elif pos == 'b6':
            return ['b4', 'd6']
        elif pos == 'c3':
            return ['c4', 'd3']
        elif pos == 'c4':
            return ['b4', 'c3', 'c5']
        elif pos == 'c5':
            return ['c4', 'd5']
        elif pos == 'd1':
            return ['a1', 'd2', 'g1']
        elif pos == 'd2':
            return ['b2', 'd1', 'd3', 'f2']
        elif pos == 'd3':
            return ['c3', 'd2', 'e3']
        elif pos == 'd5':
            return ['c5', 'd6', 'e5']
        elif pos == 'd6':
            return ['b6', 'd5', 'd7', 'f6']
        elif pos == 'd7':
            return ['a7', 'd6', 'g7']
        elif pos == 'e3':
            return ['d3', 'e4']
        elif pos == 'e4':
            return ['e3', 'e5', 'f4']
        elif pos == 'e5':
            return ['d5', 'e4']
        elif pos == 'f2':
            return ['d2', 'f4']
        elif pos == 'f4':
            return ['e4', 'f2', 'f6', 'g4']
        elif pos == 'f6':
            return ['d6', 'f4']
        elif pos == 'g1':
            return ['d1', 'g4']
        elif pos == 'g4':
            return ['f4', 'g1', 'g7']
        elif pos == 'g7':
            return ['d7', 'g4']
        else:
            return []


    def getMillMoves(self, state, A, sq, p):
        # helper function- returns None if no new mill is formed by move
        # otherwise, returns all possible moves with given 'A B '
        # first, check if it makes a mill
        theBoard = state.board.copy()
        oldMills = 0
        for mill in Lasker_Morris.MILL_LIST:
            if all(theBoard[x] == p for x in mill):
                oldMills += 1
        newBoard = theBoard.copy()
        newBoard[sq] = p
        newMills = 0
        for mill in Lasker_Morris.MILL_LIST:
            if all(newBoard[x] == p for x in mill):
                newMills += 1
        if (oldMills == newMills):
            # returning None if there are no new mills formed by move
            return None
        
        # now we know it creates a mill, so 
        # 1- check all opp positions on new board
        # 2- check number of opp mills- if all stones are in mills, add all stones,
        # but if some are in mills, add the non-mills
        opp = 'blue'
        if p == 'blue':
            opp = 'orange'
        oppSquares = []
        for x, y in newBoard.items():
            if y == opp:
                oppSquares.append(x)
        # get all oppSquares are in mills
        notMilled = []
        for sq in oppSquares:
            isMill = False
            for mill in Lasker_Morris.MILL_LIST:
                if sq in mill and all(newBoard[x] == opp for x in mill):
                    isMill = True
                    break
            if not isMill:
                notMilled.append(sq)

        # if all milled, return all moves with oppSquares
        # otherwise, return all moves with notMilled
        if len(notMilled) == 0:
            return [f'{A} {sq} {z}' for z in oppSquares]
        else:
            return [f'{A} {sq} {z}' for z in notMilled]
        

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
    player_id = input().strip()
    first_move_made = 0
    LM = Lasker_Morris()
    theState = LM.initial #gamestate
    blueRemoved = 0
    orangeRemoved = 0

    while True:
        # first move logic
        if player_id == "blue" and first_move_made == 0:
            moveX1 = (alpha_beta_search(theState, LM)) #get best 1st move as X
            # update internal board with our move
            tac = Lasker_Morris.result(tic, tac, moveX1)
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
                tac = Lasker_Morris.result(tic, tac, translated_op_inputX)
                if tac == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                moveO1 = alpha_beta_search(tac, tic) #get best move as O
                tac = Lasker_Morris.result(tic, tac, moveO1)
                print(tuple_translate(moveO1), flush=True)
                #check for orange win and terminate if win is found
                if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 1:
                    print("GAME OVER: orange player wins!")
                    sys.exit(0)


            # Read opponent's move
            opponent_inputO = input().strip() #opponent move as O
            translated_op_inputO = string_translate(opponent_inputO)
            if translated_op_inputO == "INVALID":
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
            print(tuple_translate(moveX2), flush=True)
            # check for blue win and terminate if win is found
            if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 1:
                print("GAME OVER: blue player wins!")
                sys.exit(0)

            if Lasker_Morris.terminal_test(tic, tac) and tac.utility == 0:
                print("GAME OVER: it's a draw!")
                sys.exit(0)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
