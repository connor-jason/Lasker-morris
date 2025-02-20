# Lasker Morris

# The names of the members of your group. 
Peter Cancilla, Abby Haller, Connor Jason

## A detailed description of what each teammate contributed to the project.
Abby: Wrote logic for determining moves by writing Actions, and helper functions adj and getMillMoves for actions. Debugging work later on.
Connor: Wrote many of the helper functions found in the code. Helped make the iterative deepening search work properly. Made the utility function. Refactored a lot of the code for optimization & readability. Debugged errors for invalid moves. Wrote a lot of documentation.
Peter: Wrote player logic for interacting with the referee. Wrote inital implementation of alpha-beta-search with iterative deepening. Added in Draw condition.

# Instructions on compiling and running your program.
To run in terminal:
``` python Lake_Morts.py ```

To run with referee:
``` cs4341-referee laskermorris -p1 "python Lake_Morts.py" -p2 "python Lake_Morts.py" --visual ```

# The utility function that your program uses.
Our utility function is called utility. It gives each board state a value based on how much/little it benefits the player. It's heavily weighed to favor the creation and blocking of mills, but also takes into account which board spaces are seem as "favorable" to take in the beginning of the game, the amount of pieces placed on the board, and the amount of legal moves you can make from that board state. If a board is considered "winning" or "losing", then it will just return a really big or really small value to ensure those boards are handled appropriately.

# The evaluation function that your program uses.
Our utility function essentially doubles as our evaluation function. It is used inside of the minimax alpha-beta pruning algorithm to decide which moves are good and which are bad.

# The heuristics and/or strategies that you employed to decide how to expand nodes of the minimax tree without exceeding your time limit.
Iterative deepening, alpha-beta pruning, sorting the list of moves by which may be "most promising", time management checks, and memoization of past boards to avoid recomputation.

# Results: 

## describe which tests you ran to try out your program. 

### Did your program play against human players? 
Yes, in the terminal you are able to play against the program.

### Did your program play against itself? 
Yes, with referee we were able to play the program against itself.

### Did your program play against other programs?
No.

### How did your program do during those games? 
During the games where the program played itself, it usually ends in a draw.
When playing against a human, the program usually won or ended in a draw.

### Describe the strengths and the weaknesses of your program.
Strengths:
It plays the game pretty well. It factors in a lot of important aspects of the game to determine different winning and losing states and acting accordingly. And, we haven't had it go over the time limit which is good.
Weaknesses:
The algorithm runs pretty slow. Even with optimizations, Python, by nature, is pretty slow. If we chose to write this in something like C or Java, we would be able to check signifcantly more boards.

# A discussion of why the evaluation function and the heuristic(s) you picked are good choices
- Evaluation function
Our utility function was designed to include as many different elements of Lasker Morris as possible to give our algorithm the best chance at "learning" to play the game. When doing our own testing, we found this to be creating/blocking mills, taking the most versatile squares, and having a lot of possible moves to make.
- Heuristics
We uses iterative deepening in our minimax algorithm to ensure we check as many boards as possible without exceeding the time limit. After this, we tried to optimize the algorithm to go as deep as we can. This included things like alpha-beta pruning, ordering the moves to check the ones that are the most "promising", and memoizing already computed boards to avoid recomputing the same thing many times on the same level. How we determined which boards were "promising" was pretty simple: we just ordered them by which ones remove an opponents piece or not. This was an extremely lightweight way of picking good moves while avoiding expensive computations.