import math
import sys
from collections import namedtuple
from time import time

#Code from Textbook with some minor modifications
GameState = namedtuple('GameState', 'to_move, utility, board, moves, removed, stalemate_count')
time_limit = 5  # seconds
stalemate_threshold = 20
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
        moves = [f"{x} {y} {z}" for x in ['h1'] 
                 for y in self.positions 
                 for z in ['r0']]
        
        removed = {'blue': 0, 'orange': 0}
        self.initial = GameState(to_move='blue', utility=0, board=board, moves=moves, removed=removed, stalemate_count = 0)

        # Precompute which mills each position is in
        self.mills_by_position = self.compute_mills_by_position()

    def compute_mills_by_position(self):
        """
        Precomputes mills by position for faster mill checking
        """
        mills_by_pos = {pos: [] for pos in self.positions}
        for mill in Lasker_Morris.MILL_LIST:
            for pos in mill:
                mills_by_pos[pos].append(mill)
        return mills_by_pos

    def actions(self, state):
        """Return a list of the legal moves at this point."""
        # This will depend on a lot of factors:
        # Current player- blue or orange
        curPlayer = state.to_move

        # Current players # of stones in hand, on board, removed
        boardStones = sum(1 for pos, val in state.board.items() if val == curPlayer)

        # Unsure how to keep track of # of stones removed? For now, it will be passed as arg
        stonesRemoved = state.removed[curPlayer]
        handStones = 10 - (boardStones + stonesRemoved)

        # If number of stones to play is <=2, other player wins, so return no moves
        if (handStones == 0 and boardStones <= 2):
            return []

        # Empty squares on board
        emptySquares = [pos for pos, occupant in state.board.items() if occupant is None]

        # This list will be in ['h1 a4 r0', 'd1 a4 e5'] etc format
        moves = []
        
        # Create moves here:
        # If hand > 0, for each empty square:
        # Add it to moves 'h1/h2 square r0' (and also check for mills)
        if (handStones > 0):
            hand = 'h1' if curPlayer == 'blue' else 'h2'
            for sq in emptySquares:
                millMoves = self.getMillMoves(state, hand, sq, curPlayer)
                # if no mill is created:
                if millMoves is None:
                    moves.append(f'{hand} {sq} r0')
                else:
                    moves.extend(millMoves)
                
        # If boardStones > 3
        # For each current square, check all adjacent squares
        # Only add move if the adj square is empty
        # need to check for mills though also
        if boardStones != 3 and boardStones > 0:
            pSquares = [pos for pos, occupant in state.board.items() if occupant == curPlayer]
            for sq in pSquares:
                # helper to return all adj sq's
                # then, remove all adjs that are NOT empty
                adjSqs = [adj for adj in self.adj(sq) if state.board[adj] is None]
                for adj in adjSqs:
                    millMoves = self.getMillMoves(state, sq, adj, curPlayer)
                    if millMoves is None:
                        moves.append(f'{sq} {adj} r0')
                    else:
                        moves.extend(millMoves)

        # If hand == 0, boardStones == 3: pieces can fly
        # Thus, add all emptySquares 'd1 square r0' (and also check for mills)
        if boardStones == 3 and handStones == 0:
            pSquares = [pos for pos, occupant in state.board.items() if occupant == curPlayer]
            for sq in pSquares:
                for empty in emptySquares:
                    millMoves = self.getMillMoves(state, sq, empty, curPlayer)
                    if millMoves is None:
                        moves.append(f'{sq} {empty} r0')
                    else:
                        for move in millMoves:
                            moves.append(move)

        # This is designed to be exhaustive - send back every single specific valid move
        return moves

    def adj(self, pos):
        # helper function to return all adjacent sqs to sq
        adjacent = {
            'a1': ['a4', 'd1'],
            'a4': ['a1', 'a7', 'b4'],
            'a7': ['a4', 'd7'],
            'b2': ['b4', 'd2'],
            'b4': ['a4', 'b2', 'b6', 'c4'],
            'b6': ['b4', 'd6'],
            'c3': ['c4', 'd3'],
            'c4': ['b4', 'c3', 'c5'],
            'c5': ['c4', 'd5'],
            'd1': ['a1', 'd2', 'g1'],
            'd2': ['b2', 'd1', 'd3', 'f2'],
            'd3': ['c3', 'd2', 'e3'],
            'd5': ['c5', 'd6', 'e5'],
            'd6': ['b6', 'd5', 'd7', 'f6'],
            'd7': ['a7', 'd6', 'g7'],
            'e3': ['d3', 'e4'],
            'e4': ['e3', 'e5', 'f4'],
            'e5': ['d5', 'e4'],
            'f2': ['d2', 'f4'],
            'f4': ['e4', 'f2', 'f6', 'g4'],
            'f6': ['d6', 'f4'],
            'g1': ['d1', 'g4'],
            'g4': ['f4', 'g1', 'g7'],
            'g7': ['d7', 'g4']
        }
        return adjacent.get(pos, [])

    def getMillMoves(self, state, current_square, target_square, player):
        # helper function- returns None if no new mill is formed by move
        # otherwise, returns all possible moves with given 'A B '
        # first, check if it makes a mill
        oldBoard = state.board.copy()
        newBoard = oldBoard.copy()        
        
        if current_square.startswith('h'):
            # Placement move
            newBoard[target_square] = player
        else:
            # Flying move
            newBoard[target_square] = player
            newBoard[current_square] = None

        # For placement moves you need the sq, for moving moves you need the target spot
        target = target_square if current_square.startswith('h') else current_square

        # Check for mills that include the target spot
        mills_involving_target = self.mills_by_position[target]
        
        oldMills = [mill for mill in mills_involving_target if all(oldBoard[pos] == player for pos in mill)]
        newMills = [mill for mill in mills_involving_target if all(newBoard[pos] == player for pos in mill)]

        # If at least one new mill is formed, you need to make a move that removes a piece
        if any(mill not in oldMills for mill in newMills):
            opponent = 'orange' if player == 'blue' else 'blue'

            opponent_positions = [pos for pos, mark in newBoard.items() if mark == opponent]

            # get all oppSquares are in mills
            notMilled = [
                pos for pos in opponent_positions
                    if not any(pos in mill and all(newBoard[x] == opponent for x in mill)
                            for mill in Lasker_Morris.MILL_LIST)
            ]

            # if all milled, return all moves with oppSquares
            # otherwise, return all moves with notMilled
            if not notMilled:
                return [f'{current_square} {target_square} {z}' for z in opponent_positions]
            
            return [f'{current_square} {target_square} {z}' for z in notMilled]
        return None
        
    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        # Parse the move into 3 parts
        try:
            partA, partB, partC = move.split()
        except ValueError:
            return "INVALID" # Move doesn't have 3 parts
        
        # Create a new board with the new move
        new_board = state.board.copy()
        current_player = state.to_move
        opponent = 'orange' if current_player == 'blue' else 'blue'
        new_removed = state.removed.copy()

        # If this is a removal move (partC is not r0), remove the piece
        if partC != "r0":
            new_stalemate_count = 0
            # Validate that the move is valid
            if new_board.get(partC) != opponent:
                return "INVALID"
            # Remove the opponent's piece
            new_board[partC] = None
            new_removed[opponent] += 1
        else:
            new_stalemate_count = state.stalemate_count + 1

        # In a placement move, partA is a hand marker and partB is the target
        # In a moving/flying move, partA is the start and partB is the end
        # If partA starts with 'h', it's a placement, else it's a flying move
        if partA.startswith('h'):
            # Placement move
            if new_board.get(partB) is not None:
                return "INVALID"
            new_board[partB] = current_player
        else:
            # Flying move
            if new_board.get(partA) != current_player or new_board.get(partB) is not None:
                return "INVALID"
            new_board[partA] = None
            new_board[partB] = current_player

        # Check if a mill was formed
        mills_involving_target = self.mills_by_position.get(partB, [])
        # Compute the mills that were present before making the move
        oldMills = [mill for mill in mills_involving_target if all(state.board.get(pos) == current_player for pos in mill)]
        # Compute the mills present after making the move
        newMills = [mill for mill in mills_involving_target if all(new_board.get(pos) == current_player for pos in mill)]
        # If a new mill is formed but no removal was specified, the move is invalid
        if any(mill not in oldMills for mill in newMills) and partC == "r0":
            return "INVALID"
            
        # Remove the move from the list of available moves
        new_moves = [m for m in state.moves if m != move]

        # Switch to the other player
        next_player = opponent

        # Create a new state with a utility of 0 then update it by using the utility function
        new_state = GameState(to_move=next_player, utility=0, board=new_board, moves=new_moves, removed=new_removed, stalemate_count=new_stalemate_count)
        new_state = new_state._replace(utility=self.utility(new_state, new_state.to_move))

        return new_state

    def utility(self, state, player):
        """Return the value of this final state to player."""

        opponent = 'blue' if player == 'orange' else 'blue'

        # If the game is over, return a high or low value
        if self.terminal_test(state):
            if self.check_win(state, player):
                return 1000
            elif self.check_win(state, opponent):
                return -1000
            elif state.stalemate_count == stalemate_threshold:
                return 0
        
        # Determine the game phase
        boardStones = sum(1 for pos in state.board if state.board[pos] == player)
        handStones = 10 - (boardStones + state.removed[player])
        if handStones > 0:
            phase = 'placement'
        elif boardStones == 3:
            phase = 'flying'
        else:
            phase = 'moving'

        # Set weights based on the game phase, weights are pretty arbitrary and are just my best guess
        if phase == 'placement':
            weight_mills = 20
            weight_potential = 14
            weight_pieces = 5
            weight_moves = 0.5
        elif phase == 'moving':
            weight_mills = 15
            weight_potential = 6
            weight_pieces = 2
            weight_moves = 1
        else: # flying phase
            weight_mills = 10
            weight_potential = 4
            weight_pieces = 2.5
            weight_moves = 1.5

        # Optimal board position weights during the placement phase, weights are pretty arbitrary and are just my best guess
        position_weights = {
            # Row 1
            "a1": 0.8,
            "d1": 1.0,
            "g1": 0.8,

            # Row 2
            "b2": 1.0,
            "d2": 1.4, # Next to d3 intersection
            "f2": 1.0,

            # Row 3
            "c3": 1.2, # Corner of inner square
            "d3": 2.5, # Intersection
            "e3": 1.2, # Corner of inner square

            # Row 4
            "a4": 1.0,
            "b4": 1.4, # Next to c4 intersection
            "c4": 2.5, # Intersection
            "e4": 2.5, # Intersection
            "f4": 1.4, # Next to e4 intersection
            "g4": 1.0,

            # Row 5
            "c5": 1.2, # Corner of inner square
            "d5": 2.5, # Intersection
            "e5": 1.2, # Corner of inner square

            # Row 6
            "b6": 1.0,
            "d6": 1.4, # Next to d5 intersection
            "f6": 1.0,

            # Row 7
            "a7": 0.8,
            "d7": 1.0,
            "g7": 0.8
        }

        # Compute positional bonus during placement phase
        if phase == 'placement':
            positional_player = sum(position_weights.get(pos, 1.0) for pos in state.board if state.board[pos] == player)
            positional_opponent = sum(position_weights.get(pos, 1.0) for pos in state.board if state.board[pos] == opponent)
            pos_score = 4 * (positional_player - positional_opponent)
        else:
            pos_score = 0

        # Count the number of mills for each player
        mills_player = 0
        mills_opponent = 0
        for mill in Lasker_Morris.MILL_LIST:
            if all(state.board[pos] == player for pos in mill):
                mills_player += 1
            elif all(state.board[pos] == opponent for pos in mill):
                mills_opponent += 1

        # Count potential mills (2 in a row with one empty spot)
        potential_mills_player = 0
        potential_mills_opponent = 0
        for mill in Lasker_Morris.MILL_LIST:
            pieces_player = sum(1 for pos in mill if state.board[pos] == player)
            pieces_opponent = sum(1 for pos in mill if state.board[pos] == opponent)
            empty = sum(1 for pos in mill if state.board[pos] is None)
            if pieces_player == 2 and empty == 1:
                potential_mills_player += 1
            if pieces_opponent == 2 and empty == 1:
                potential_mills_opponent += 1

        # Count the number of pieces for each player
        pieces_player = sum(1 for pos in state.board if state.board[pos] == player)
        pieces_opponent = sum(1 for pos in state.board if state.board[pos] == opponent)

        # Count the number of legal moves available for each player
        legal_moves_player = len(self.actions(state))

        opponent_state = state._replace(to_move=opponent)
        legal_moves_opponent = len(self.actions(opponent_state))

        # Combine the values into a single score (very mill focused)
        score = (weight_mills * (mills_player - mills_opponent) +
                weight_potential * (potential_mills_player - potential_mills_opponent) +
                weight_pieces * (pieces_player - pieces_opponent) +
                weight_moves * (legal_moves_player - legal_moves_opponent) +
                pos_score)
        
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
        # Determine the opponent
        opponent = 'orange' if player == 'blue' else 'blue'
        
        # Count opponents pieces on the board
        opp_pieces = sum(1 for pos in state.board if state.board[pos] == opponent)
        if opp_pieces < 3:
            return True
        
        # Create a simulated state where its the opponents turn to check their moves
        opponent_state = state._replace(to_move=opponent)
        
        # If the opponent has no moves left they lose
        if len(self.actions(opponent_state)) == 0:
            return True
        
        return False

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        if state.stalemate_count == stalemate_threshold:
            return True
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

def memoize_states(state):
    # Memoize the state's board, removed counts, and turn
    board_tuple = tuple(sorted(state.board.items()))
    removed_tuple = tuple(sorted(state.removed.items()))
    return (state.to_move, board_tuple, removed_tuple)

def alpha_beta_deepening_search(state, game):
    start_time = time()
    safe_margin = 0.02  # Send the move 0.02 seconds before the time limit
    best_action = None
    depth = 1
    memo_states = {} # Store the state and its values at a certain depth

    # Continue deepening until we hit the time limit
    while time() - start_time < time_limit - safe_margin:
        current_best = alpha_beta_search(state, game, depth, start_time, memo_states, safe_margin)
        if current_best is not None:
            best_action = current_best
        depth += 1

    if best_action is None:
        actions = game.actions(state)
        if actions:
            best_action = actions[0]

    return best_action

def alpha_beta_search(state, game, depth, start_time, memo_states, safe_margin):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = game.to_move(state)
    
    # Sort moves that remove an opponent piece to the beginning
    def order_moves(moves, reverse=False):
        return sorted(moves, key=lambda move: 1 if move.split()[2] != "r0" else 0, reverse=reverse)
    
    def max_value_ab(state, alpha, beta, depth):
        # Check if we are near the time limit
        if time() - start_time > time_limit - safe_margin:
            return game.utility(state, player)
        
        # Check if the state is terminal or if we have reached the root
        if game.terminal_test(state) or depth <= 0:
            return game.utility(state, player)
        
        # If the state has already been evaluated at this depth, return the value
        state_key = memoize_states(state)
        if state_key in memo_states and memo_states[state_key][1] >= depth:
            return memo_states[state_key][0]
        
        v = -math.inf
        # Check high utility first
        for a in order_moves(game.actions(state), reverse=True):
            if time() - start_time > time_limit - safe_margin:
                break
            result_state = game.result(state, a)
            if result_state == "INVALID":
                continue
            # Recursively call min_value
            v = max(v, min_value_ab(result_state, alpha, beta, depth - 1))
            # Beta pruning
            if v >= beta:
                memo_states[state_key] = (v, depth) # Cache the value
                return v
            alpha = max(alpha, v)
        memo_states[state_key] = (v, depth) # Cache the value
        return v

    def min_value_ab(state, alpha, beta, depth):
        # Check if we are near the time limit
        if time() - start_time > time_limit - safe_margin:
            return game.utility(state, player)
        
        # Check if the state is terminal or if we have reached the root
        if game.terminal_test(state) or depth <= 0:
            return game.utility(state, player)
        
        # If the state has already been evaluated at this depth, return the value
        state_key = memoize_states(state)
        if state_key in memo_states and memo_states[state_key][1] >= depth:
            return memo_states[state_key][0]
        
        v = math.inf
        # Check low utility moves first
        for a in order_moves(game.actions(state), reverse=False):
            if time() - start_time > time_limit - safe_margin:
                break
            result_state = game.result(state, a)
            if result_state == "INVALID":
                continue
            # Recursively call max_value
            v = min(v, max_value_ab(result_state, alpha, beta, depth - 1))
            # Alpha pruning
            if v <= alpha:
                memo_states[state_key] = (v, depth) # Cache the value
                return v
            beta = min(beta, v)
        memo_states[state_key] = (v, depth) # Cache the value
        return v

    best_score = -math.inf
    beta = math.inf
    best_action = None
    for a in order_moves(game.actions(state), reverse=True):
        # Check if we are near the time limit
        if time() - start_time > time_limit - safe_margin:
            break
        result_state = game.result(state, a)
        if result_state == "INVALID":
            continue
        v = min_value_ab(result_state, best_score, beta, depth - 1)
        # Keep the best action
        if v > best_score:
            best_score = v
            best_action = a
    return best_action

def main():
    # Read initial color/symbol
    player_id = input().strip()
    first_move_made = 0
    LM = Lasker_Morris()
    theState = LM.initial  # gamestate

    while True:
        # first move logic
        if player_id == "blue" and first_move_made == 0:
            moveX1 = alpha_beta_deepening_search(theState, LM)  # get best 1st move as X
            # update internal board with our move
            theState = LM.result(theState, moveX1)
            first_move_made += 1
            print(moveX1, flush=True)  # send move to referee

        try:
            if player_id == "orange":
                # Read opponent's move
                opponent_inputX = input().strip()  # opponent move as X/blue
                # update internal board with opponent move
                theState = LM.result(theState, opponent_inputX)
                if theState == "INVALID":
                    print("blue player has played an invalid move; orange player wins!", flush=True)
                    sys.exit(0)
                moveO1 = alpha_beta_deepening_search(theState, LM)  # get best move as O
                theState = LM.result(theState, moveO1)
                print(moveO1, flush=True)
                # check for orange win and terminate if win is found
                if LM.terminal_test(theState) and theState.utility == 100:
                    print("GAME OVER: orange player wins!")
                    sys.exit(0)

            # Read opponent's move
            opponent_inputO = input().strip()  # opponent move as O
            # update internal board with opponent move
            theState = LM.result(theState, opponent_inputO)
            if theState == "INVALID":
                print("orange player has played an invalid move; blue player wins!", flush=True)
                sys.exit(0)
            # Move logic
            moveX2 = alpha_beta_deepening_search(theState, LM)  # get best move as X
            theState = LM.result(theState, moveX2)
            # Send move to referee
            print(moveX2, flush=True)
            # check for blue win and terminate if win is found
            if LM.terminal_test(theState) and theState.utility == 100:
                print("GAME OVER: blue player wins!")
                sys.exit(0)

            if LM.terminal_test(theState) and theState.utility == 0:
                print("GAME OVER: it's a draw!")
                sys.exit(0)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)

if __name__ == "__main__":
    main()
