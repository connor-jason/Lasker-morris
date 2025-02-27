# Lasker Morris

# Instructions on compiling and running your program.
To run in terminal:
``` python Lake_Morts.py ```

To run with referee:
``` cs4341-referee laskermorris -p1 "python Lake_Morts_LLM.py" -p2 "python Lake_Morts_LLM.py" --visual -t 60```

# System Description

# Prompt Engineering
Here are all the different prompts we had at one point in our repo:
## Prompt variation 1
```
intro = "Hello, you are playing a game of Lasker Morris. The rules will be summarized below: There are two players: blue and orange. Each player has 10 stones in their hand at the start of the game. The initial board is set up as so: [a1: None, a4: None, a7: None, b2: None, b4: None, b6: None, c3: None, c4: None, c5: None, d1: None, d2: None, d3: None, d5: None, d6: None, d7: None, e3: None, e4: None, e5: None, f2: None, f4: None, f6: None, g1: None, g4: None, g7: None]. A mill is formed when three stones of the same color are placed on the board that are aligned contiguously vertically or horizontally. Here is the list of mill combinations: (a1, a4, a7), (a7, d7, g7), (g7, g4, g1), (a1, d1, g1), (b2, d2, f2), (b2, b4, b6), (b6, d6, f6), (f6, f4, f2), (a4, b4, c4), (e4, f4, g4), (d1, d2, d3), (d5, d6, d7), (c3, d3, e3), (c3, c4, c5), (c5, d5, e5), (e5, e4, e3)."
curInfo = "You are currently playing as " + player + " player. This is your board configuration: " + str(board) + ". You have " + str(handStones) + " stones in your hand. Here is your list of moves: " + str(moves) + ". Please produce the next best move from this list of moves, and tell us the move in (A B C) format: for example, (h1 d2 r0)."
return intro + " " + curInfo
```
### Findings
This prompt was kind of long and had a lot of "fluff" that wasted tokens. The model made pretty bad moves and we thought it was because the prompt wasn't direct and clear enough.

## Prompt variation 2
```
mill_combinations = "(a1, a4, a7), (a7, d7, g7), (g7, g4, g1), (a1, d1, g1), (b2, d2, f2), (b2, b4, b6), (b6, d6, f6), (f6, f4, f2), (a4, b4, c4), (e4, f4, g4), (d1, d2, d3), (d5, d6, d7), (c3, d3, e3), (c3, c4, c5), (c5, d5, e5), (e5, e4, e3)"

rules = (
    "You are playing a game of Lasker Morris. Here are the rules:\n" 
    "1. There are two players. Each player starts with 10 stones.\n"
    "2. A valid move is in the format (A B C):\n"
    "- A: Current location (either hand ('h1'/'h2'), or a board position occupied by a stone of yours you wish to move).\n"
    "- B: Target empty board position.\n"
    "- C: 'r0' normally, or the position of an opponent's stone to remove if a new mill is formed.\n"
    "3. A mill is a very powerful type of move. A mill allows you to remove a stone placed by your opponent. One is formed when three stones from the same player occupy one of the following sets of positions:\n" 
    + mill_combinations + "\n"
)

current_state = (
    f"Current Player: {player}\n"
    f"Board: {board}\n"
    f"Stones in Hand: {handStones}\n"
    f"Available Moves: {moves}\n"
)

instructions = (
    "Please perform the following:\n"
    "1. Provide your logical reasoning for which move to select, explaining your thought process using the game state information provided.\n"
    "2. At the end, output the final move in (A B C) format (for example, 'h1 d2 r0') without any extra commentary.\n"
    "Remember: Your reasoning should be detailed, but the final output must be a single valid move from the list of available moves."
)

return rules + "\n" + current_state + "\n" + instructions
```

### Findings
This prompt was better. It removed some of the fluff, and organized the information in a much more clear and structured way. We found that putting the models "tasks" at the end seemed to work best and be the most consistent. But, some of the details could be more clear to try to minimize invalid moves or poor gameplay. We didn't want to give it too much strategy because we wanted to see what it thought was the best way to play, but we did teach it about the power of mills since it's a key part of the game.

## Final Prompt
```
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
    "1. Provide your logical reasoning for which move to select, explaining your thought process using the game state information provided. Prioritize moves that make a mill.\n"
    "2. At the end, output the final move in (A B C) format (for example, 'h1 d2 r0') without any extra commentary.\n"
    "Remember: Your reasoning should be detailed, but the final output must be a single valid move from the list of available moves."
)

return rules + "\n" + current_state + "\n" + instructions
```

### Findings
This prompt was the final one we decided on after a few other minor tweaks. We made the information it needed as clear as possible to minimize confusion and to hopefully allow it to play as optimally as it's capable of. We found that this prompt was pretty good. Using LLMs like this won't ever be "great" (right now, at least), but we found that this one was pretty good as far as prompts go.

# Testing & Results: 

## describe which tests you ran to try out your program. 

### Did your program play against human players? 
Yes, in the terminal you are able to play against the program.

### Did your program play against itself? 
Yes, with referee we were able to play the program against itself.

### Did your program play against other programs?
No.

### How did your program do during those games? 
It doesn't play extremely intelligently. It really only tries to form mills, which is what we told it to do, but there really is no thought about strategy other than that. This causes the games to become very boring and predictable.

### Are LLMs good at game-playing?
No, not yet. Eventually they may be, but right now this is not within their skillset. Especially with a model like Gemini Flash that is unable to use chain-of-thought reasoning, it really struggles to play a game like this even remotely well.