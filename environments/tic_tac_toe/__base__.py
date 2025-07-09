"""# lucidium.environments.tic_tac_toe.base

Defines the Tic Tac Toe game framework.
"""

from typing                 import Any, Dict, List, override, Tuple, Union

from numpy                  import ndarray
from torch                  import Tensor

from .components            import *
from environments.__base__  import Environment
from spaces                 import Box, Discrete
from symbolic               import Predicate

class TicTacToe(Environment):
    """# Tic-Tac-Toe (Environment)
    
    Tic-Tac-Toe is a two-player game where players take turns marking a square in a 3x3 grid. The 
    first player to align three of their marks horizontally, vertically, or diagonally wins the 
    game.
    """
    
    def __init__(self,
        size:                   int =    3,
        win_reward:             float =  1.0,
        loss_penalty:           float = -1.0,
        draw_reward:            float =  0.0,
        invalid_move_penalty:   float = -0.5,
        move_penalty:           float = -0.1,
        **kwargs
    ):
        """# Instantiate Tic-Tac-Toe Environment

        ## Args:
            * size                  (int, optional):    Size of (square) board. Defaults to 3.
            * win_reward            (float, optional):  Reward yielded from winning a game. Defaults 
                                                        to 1.0.
            * loss_penalty          (float, optional):  Penalty incurred by losing a game. Defaults 
                                                        to -1.0.
            * draw_reward           (float, optional):  Reward yielded by ending game in a draw 
                                                        (neither player wins). Defaults to 0.0.
            * invalid_move_penalty  (float, optional):  Penalty incurred for attempting an invalid 
                                                        move. Defaults to -0.5.
            * move_penalty          (float, optional):  Cost of making a single move. Defaults to 
                                                        -0.1.
        """
        # Define environment properties
        self._size_:                    int =       size
        self._win_reward_:              float =     win_reward
        self._loss_penalty_:            float =     loss_penalty
        self._draw_reward_:             float =     draw_reward
        self._invalid_move_penalty_:    float =     invalid_move_penalty
        self._move_penalty_:            float =     move_penalty
        
        # Define action space.
        self._action_space_:            Discrete =  Discrete(n = size ** 2)
        
        # Define observation space.
        self._observation_psace_:       Box =       Box(lower = -1, upper = 1, shape = (3, size, size))
        
        # Instantiate board.
        self._board_:                   Board =     Board(size = size)
        
        # Define players.
        self._player_x_:                Player =    Player.from_symbol("X")
        self._player_o_:                Player =    Player.from_symbol("O")
        self._current_player_:          Player =    self._player_x_
        
    # PROPERTIES ===================================================================================
    
    # METHODS ======================================================================================
    
    @override
    def reset(self) -> Union[Tensor, List[Predicate]]:
        """# Reset (Environment).
        
        Reset environment to initial state.

        ## Returns:
            * Union[Tensor, List[Predicate]]:   Observation of environment state after reset.
        """
        # Reset board.
        self._board_.reset()
        
        # Provide observation.
        return self.observe()
    
    @override
    def step(self,
        action: int
    ) -> Tuple[Union[Tensor, List[Predicate]], float, bool, Dict[str, Any]]:
        """# Step
        
        Update environment based on action submitted.

        ## Args:
            * action    (int):  Action submitted by agent.

        ## Returns:
            * Tuple[Union[Tensor, List[Predicate]], float, bool, Dict[str, Any]]:
                * Updated state after action
                * Reward yielded/penalty incurred by action
                * True if environment has reached a terminal state
                * Metadata
        """
        # If game has already concluded, an action cannot be submitted.
        if self._done_: raise RuntimeError(f"Game has already concluded.")
        
        # If entry is marked...
        if self._board_.mark_by_index(index = action, entry = self._current_player_.symbol):
            
            # If move resulted in a win, assign reward.
            if self._board_.has_winner: return  self.observe(),     \
                                                self._win_reward_,  \
                                                True,               \
                                                {"event": "won the game"}
        
        # Otherwise, assign penalty for invalid move.
        return self.observe(), self._move_penalty_, False, {"event": "attempted invalid move"}
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation"""
        return f"""TicTacToe(size = {self._size_})"""
    
    def __str__(self) -> str:
        """# String Representation"""
        return str(self._board_)