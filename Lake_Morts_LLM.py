import math
import sys
from collections import namedtuple
from time import time, sleep
import os
from dotenv import load_dotenv
from google import genai
import re

# Load .env vars
load_dotenv()

# Get API key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def call_llm(prompt):
    sleep(4.5)
    response = client.models.generate_content(
         model="gemini-2.0-flash", contents=prompt
    )
    return response.text

def extract_move(response_text):
    """
    Regex looks for: "h1 d2 r0" or "a4 d5 r0" format with a space in between
    Explanation for ur clarity:
    - ?: lets you group alternatives together separated by |
    - h[12] matches h1 or h2
    - [a-g][1-7] matches a1, a2, b1, b2, etc.
    - r0 matches r0
    - \s+ matches one or more whitespace characters
    """
    pattern = r'((?:h[12]|[a-g][1-7])\s+(?:[a-g][1-7])\s+(?:r0|[a-g][1-7]))'
    matches = re.findall(pattern, response_text)
    if matches:
        # Return the last occurrence found, should be the "final choice" by the model
        return matches[-1].strip()
    else:
        return None

#Code from Textbook with some minor modifications
GameState = namedtuple('GameState', 'to_move, utility, board, moves, removed, stalemate_count')
time_limit = 60  # seconds
stalemate_threshold = 20
safe_margin = 12  # 10 second safe margin
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
                    # call millMoves with state, square its coming from, square its going to, currentPlayer
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
            
        # Remove the move from the list of available moves
        new_moves = [m for m in state.moves if m != move]

        # Switch to the other player
        next_player = opponent

        # Create a new state with a utility of 0 then update it by using the utility function
        new_state = GameState(to_move=next_player, utility=0, board=new_board, moves=new_moves, removed=new_removed, stalemate_count=new_stalemate_count)
        new_state = new_state._replace(moves=self.actions(new_state))
        newest_state = new_state._replace(utility=self.utility(new_state, new_state.to_move))

        return newest_state

    def utility(self, state, player):
        opponent = 'blue' if player == 'orange' else 'orange'
        if self.terminal_test(state):
            if self.check_win(state, player):
                return 1000 # win for the current player
            elif self.check_win(state, opponent):
                return -1000 # loss for the current player
            else:
                return 0  # tie/stalemate
        return 1 # non-terminal states get an arbitrary value

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

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


def makePrompt(state):
    # ('GameState', 'to_move, utility, board, moves, removed, stalemate_count')
    player = state.to_move
    board = state.board
    boardStones = sum(1 for pos, val in state.board.items() if val == player)
    stonesRemoved = state.removed[player]
    handStones = 10 - (boardStones + stonesRemoved)
    moves = state.moves

    mill_combinations = "(a1, a4, a7), (a7, d7, g7), (g7, g4, g1), (a1, d1, g1), (b2, d2, f2), (b2, b4, b6), (b6, d6, f6), (f6, f4, f2), (a4, b4, c4), (e4, f4, g4), (d1, d2, d3), (d5, d6, d7), (c3, d3, e3), (c3, c4, c5), (c5, d5, e5), (e5, e4, e3)"

    rules = (
        "You are playing a game of Lasker Morris. Here are the rules:\n" 
        "1. There are two players. Each player starts with 10 stones.\n"
        "2. A valid move is in the format (A B C):\n"
        "- A: Current location (either hand ('h1'/'h2') if you have more than 0 stones in your hand, or a board position occupied by a stone of yours you wish to move).\n"
        "- B: Target empty board position.\n"
        "- C: 'r0' normally, or the position of an opponent's stone to remove if a new mill is formed.\n"
        "3. A mill is a very powerful type of move. A mill allows you to remove a stone placed by your opponent. One is formed when three stones from the same player occupy one of the following sets of positions:\n" + mill_combinations + "\n"
        )
    
    current_state = (
        f"Current Player: {player}\n"
        f"Board: {board}\n"
        f"Stones in Hand: {handStones}\n"
        f"Available Moves: {moves}\n"
    )
    
    instructions = (
        "Please perform the following:\n"
        "1. Provide your logical reasoning for which move to select, explaining your thought process using the game state information provided. Prioritize moves that make a mill or moves that block an opponent's mill.\n"
        "2. At the end, output the final move in (A B C) format (for example, 'h1 d2 r0') without any extra commentary.\n"
        "Remember: Your reasoning should be detailed, but the final output must be a single valid move from the list of available moves."
    )

    return rules + "\n" + current_state + "\n" + instructions

# small helper for print statements
def oppPlayer(p):
    return 'blue' if p == 'orange' else 'orange'

# small helper for finding end
def endStatements(theState, LM):
    if LM.terminal_test(theState):
        match theState.utility:
            case 1000:
                print("GAME OVER: blue player wins!")
            case 0:
                print("GAME OVER: it's a draw!")
            case -1000:
                print("GAME OVER: orange player wins!")
        sys.exit(0)

def main():
    # Read initial color/symbol
    player_id = input().strip()
    LM = Lasker_Morris()
    theState = LM.initial  # gamestate

    # testing purposes
    # print(theState)
    # fakeState = GameState(to_move='blue', utility=0, board={'a1': None, 'a4': None, 'a7': None, 'b2': 'orange', 'b4': None, 'b6': None, 'c3': None, 'c4': None, 'c5': None, 'd1': 'orange', 'd2': 'blue', 'd3': 'blue', 'd5': None, 'd6': None, 'd7': None, 'e3': None, 'e4': None, 'e5': None, 'f2': 'blue', 'f4': None, 'f6': None, 'g1': 'orange', 'g4': None, 'g7': None}, 
    #           moves=['h1 a1 r0'], removed={'blue': 7, 'orange': 7}, stalemate_count=0)
    # newMove = 'd3 c3 r0'
    # theState = LM.result(fakeState, newMove)
    # print(theState)

    # first move logic
    if player_id == "blue":
        # first create prompt
        newPrompt = makePrompt(theState)
        # then pass to AI
        start_time = time()
        response = call_llm(newPrompt)
        AImove = extract_move(response)
        while AImove not in theState.moves and time()-start_time < time_limit - safe_margin:
            response = call_llm(newPrompt)
            AImove = extract_move(response)
        print(AImove, flush=True)
        # then add to gamestate
        theState = LM.result(theState, AImove)

    while True:
        try:
            # Read opponent's move
            oppMove = input().strip()  # opponent move
            opp = theState.to_move
            # update internal board with opponent move
            theState = LM.result(theState, oppMove)
            if theState == "INVALID":
                print("" + opp + " player has played an invalid move; " + oppPlayer(opp) + " player wins!", flush=True)
                sys.exit(0)
            endStatements(theState, LM)
            
            # first create prompt
            newPrompt = makePrompt(theState)
            # then pass to AI
            start_time = time()
            response = call_llm(newPrompt)
            AImove = extract_move(response)
            # Reprompt if move is invalid and still has time
            while time() - start_time < time_limit - safe_margin:
                if AImove in theState.moves and LM.result(theState, AImove) != "INVALID":
                    break  # Valid move found, exit the loop
                response = call_llm(newPrompt)
                AImove = extract_move(response)
            else:
                # No valid move was found, just choose the first one
                AImove = theState.moves[0]
            print(AImove, flush=True)
            # then add to gamestate
            theState = LM.result(theState, AImove)
            AImove = None
            if theState == "INVALID":
                print("" + opp + " player has played an invalid move; " + oppPlayer(opp) + " player wins!", flush=True)
                sys.exit(0)
            endStatements(theState, LM)

        except Exception as e:
            print("Error:", e)
            sys.exit(1)
if __name__ == "__main__":
    main()
