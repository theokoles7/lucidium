"""# lucidium.environments.tic_tac_toe.components.board

Defines the Tic Tac Toe board component.
"""

from typing                                     import Any, Dict, Optional, List, Tuple

from numpy                                      import any, ndarray, zeros

from environments.tic_tac_toe.components.glyphs import Glyphs

class Board():
    """# (Tic-Tac-Toe) Board
    
    Represents the Tic Tac Toe board, which is a 3x3 grid where players can place their marks.
    """
    
    def __init__(self,
        size:   int =   3
    ):
        """# Instantiate Tic-Tac-Toe Board
        
        ## Args:
            * size  (int, optional):    Size of the board (default is 3 for a standard Tic Tac Toe 
                                        game).
        """
        # Define board properties.
        self._size_:            int =               size
        
        # Initialize game state.
        self._grid_:            ndarray =           zeros(shape = (size, size), dtype = int)
        self._current_player_:  int =               1
        
        # Define glyphs map.
        self._glyphs_:          Dict[int, Glyphs] = {
                                                        -1: Glyphs.O,
                                                        0:  Glyphs.EMPTY,
                                                        1:  Glyphs.X
                                                    }
        
        # Initialize statistics.
        self._move_count_:      int =               0
        self._game_over_:       bool =              False
        self._status_:          str =               "INCOMPLETE"
        self._winner_:          Optional[int] =     None
        
    # PROPERTIES ===================================================================================
    
    @property
    def current_player(self) -> int:
        """# Current Player (int)
        
        Returns 1 for player or -1 for opponent.
        """
        return self._current_player_
    
    @property
    def has_winner(self) -> bool:
        """# (Board) Has Winner? (bool)

        True if current player has won.
        """
        # For each possible winning line...
        for line in self.winning_lines:
            
            # Return true if current player occupies all positions.
            if all(self.grid[r, c] == self.current_player for r, c in line): return True
        
        # Otherwise, player has not won.
        return False
    
    @property
    def is_draw(self) -> bool:
        """# (Game) Is Draw? (bool)

        True if game does not have a winner, but the board is full.
        """
        return self.is_full and self.winner is None
    
    @property
    def is_full(self) -> bool:
        """# (Board) Is Full? (bool)

        Indicate if the board is full or not.
        """
        return not any(self.grid == 0)
    
    @property
    def game_over(self) -> bool:
        """# (Is) Game Over? (bool)

        True if game has a winner or ended in a draw.
        """
        return self.is_draw or self.winner is not None
    
    @property
    def grid(self) -> ndarray:
        """# Board Grid (ndarray)
        
        Returns the current state of the board as a 2D numpy array.
        """
        return self._grid_
    
    @property
    def move_count(self) -> int:
        """# Move Count (int)
        
        Total number of valid moves made by both players thus far.
        """
        return self._move_count_
    
    @property
    def size(self) -> int:
        """# Board Size (int)
        
        Returns the size of the board.
        """
        return self._size_
    
    @property
    def state(self) -> ndarray:
        """# (Board) State

        A copy of the board's current state.
        """
        return self.grid.copy()
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """# Statistics (Dict[str, Any])

        Statistics regarding game status/progress.
        """
        return  {
                    "game_over":    self.game_over,
                    "move_count":   self.move_count,
                    "status":       self.status,
                    "winner":       self.winner
                }
        
    @property
    def winner(self) -> Optional[int]:
        """# Winner (int | None)

        Winner of current game if complete and not a draw.
        """
        return self._winner_
    
    @property
    def winning_lines(self) -> List[List[Tuple[int, int]]]:
        """# Winning Lines.

        Lists of coordinates that make up possible winnings lines.
        """
        # Initialize list of lines.
        lines:  List[List[Tuple[int, int]]] =   []
        
        # Compute winning row lines.
        for r in range(self.size): lines.append([(r, c) for c in range(self.size)])
        
        # Compute winning column lines.
        for c in range(self.size): lines.append([(r, c) for r in range(self.size)])
        
        # Compute main diagonal.
        lines.append([(i, i) for i in range(self.size)])
        
        # Compute anti-diagonal.
        lines.append([(i, self.size - 1 - i) for i in range(self.size)])
        
        # Return computed winning lines.
        return lines
    
    # SETTERS ======================================================================================
    
    @current_player.setter
    def current_player(self,
        value:  int
    ) -> None:
        """# Set Current Player.
        
        Set the current player.

        ## Args:
            * value (int):  1 for player or -1 for opponent.
            
        ## Raises:
            * AssertionError:   If value is not -1 or +1.
        """
        # Assert that value is either -1 or +1.
        assert value in [-1, 1], f"Current player expected to be -1 or +1, got {value}"
        
        # Set current player.
        self._current_player_:  int =   value
        
    @game_over.setter
    def game_over(self,
        value:  bool
    ) -> None:
        """# Set Game Over."""
        self._game_over_:   bool =  value
        
    @move_count.setter
    def move_count(self,
        value:  int
    ) -> None:
        """# Set Move Count.

        ## Args:
            * value (int): Integer greater than or equal to zero.
            
        ## Raises:
            * AssertionError:   If value is not an integer greater than or equal to zero.
        """
        # Assert that value is a positive integer.
        assert 0 <= value, f"Value must be integer greater than or equal to zero, got {value}"
        
        # Set move count.
        self._move_count_:  int =   value
        
    @winner.setter
    def winner(self,
        value:  int
    ) -> None:
        """# Set Winner.

        ## Args:
            * value (int):  1 for player or -1 for opponent.
            
        ## Raises:
            * AssertionError:   If value is not -1 or +1.
        """
        # Assert that value is either -1 or +1.
        assert value in [-1, 1], f"Current player expected to be -1 or +1, got {value}"
        
        # Set current player.
        self._winner_:  int =   value
        
    # METHODS ======================================================================================
    
    def enter_move(self,
        row:    int,
        column: int
    ) -> bool:
        """# Enter Move.
        
        Enter move on board at position specified.

        ## Args:
            * row       (int):  Row at which move is being entered.
            * column    (int):  Column at which move is being entered.

        ## Returns:
            * bool: True, if move was valid.
        """
        # If move is not valid, return False.
        if not self._move_is_valid_(row = row, column = column): return False
        
        # Enter move.
        self.grid[row, column] = self.current_player
        
        # If current player has won...
        if self.has_winner:
            
            # Define winner.
            self.winner =       self.current_player
            self.game_over =    True
            
        # Otherwise, if board is full...
        elif self.is_full:
            
            # Game is a draw.
            self.winner =       self.current_player
            
        # Otherwise, game is still in progress; switch players.
        else: self._switch_player_()
        
        # Indicate that move was entered.
        return True
        
    def enter_move_by_action(self,
        action: int
    ) -> bool:
        """# Enter Move by Action.
        
        Enter move on board at position specified by action.

        ## Args:
            * action    (int):  Integer in range(0, size ** 2)

        ## Returns:
            * bool: True if action is valid.
        """
        return  self.enter_move(
                    row =       action // self.size,
                    column =    action %  self.size
                )
        
    # HELPERS ======================================================================================
    
    def _action_is_valid_(self,
        action: int
    ) -> bool:
        """# Action is Valid?
        
        Validate proposed action.

        ## Args:
            * action    (int):  Integer in range(0, size ** 2)

        ## Returns:
            * bool: True if action is valid.
        """
        return  self._move_is_valid_(
                    row =       action // self.size,
                    column =    action %  self.size
                )
    
    def _get_glyph_(self,
        value:  int
    ) -> Glyphs:
        """# Get Glyph.
        
        Provide the glyph representation of a player position.

        ## Args:
            * value (int):  Entry value for which glyph is being retrieved.

        ## Returns:
            * Glyphs:
                * "X": Player
                * "O": Opponent
                * " ": Empty
        """
        # Assert that proper integer is provided.
        assert value in [-1, 0, 1], f"Expected value of [-1, 0, 1], got {value}"
        
        # Provide glyph.
        return self._glyphs_[value]
    
    def _move_is_valid_(self,
        row:    int,
        column: int
    ) -> bool:
        """# Move is Valid?
        
        Validate proposed move.

        ## Args:
            * row       (int):  Row at which move is being entered.
            * column    (int):  Column at which move is being entered.

        ## Returns:
            * bool: True, if move was valid.
        """
        # If position is not in range return false.
        if not 0 <= row < self.size and 0 <= column < self.size: return False
        
        # Indicate that positino is not taken.
        return self.grid[row, column] == 0
        
    def _switch_player_(self) -> None:
        """# Switch Player.
        
        Flip current player value.
        """
        self.current_player = -self.current_player
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Get Representation.
        
        Provide the string representation of the Tic-Tac-Toe board.

        ## Returns:
            * str:  String representation of the Tic-Tac-Toe board.
        """
        return self.__str__()
    
    def __str__(self) -> str:
        """# Get String.
        
        Provide the string representation of the Tic-Tac-Toe board.

        ## Returns:
            * str:  String representation of the Tic-Tac-Toe board.
        """
        # Initialize column index.
        board_string:   str =   ("   ") + " ".join(f" {column} " for column in range(1, self.size + 1))
        
        # For each row in grid...
        for r, row in enumerate(self.grid, start = 1):
            
            # Start new row with index.
            board_string        +=  f"\n {r} "
            
            # For each column in grid...
            for c, column in enumerate(row, start = 1):
                
                # Append glyph.
                board_string    +=  f" {self._get_glyph_(column)} │"          \
                                        if c != self.size                   \
                                        else f" {self._get_glyph_(column)} "
                
            # Append line separator if not last row.
            board_string        +=  ("\n   " + ("───┼" * (self.size - 1)) + ("─" * 3))  \
                                        if r != self.size                               \
                                        else f""
        
        # Return board representation.
        return board_string