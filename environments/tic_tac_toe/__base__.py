"""# lucidium.environments.tic_tac_toe.base

Defines the Tic Tac Toe game framework.
"""

from typing                                 import Any, Dict, Tuple, override, Union

from numpy                                  import ndarray

from environments.__base__                  import Environment
from environments.tic_tac_toe.components    import Board

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
        self._size_:                    int =   size
        self._win_reward_:              float = win_reward
        self._loss_penalty_:            float = loss_penalty
        self._draw_reward_:             float = draw_reward
        self._invalid_move_penalty_:    float = invalid_move_penalty
        self._move_penalty_:            float = move_penalty
        
    # PROPERTIES ===================================================================================
    
    @property
    @override
    def action_space(self) -> int:
        """# Action Space

        Possible actions.
        """
        return self.size ** 2
    
    @property
    def board(self) -> Board:
        """# (Tic-Tac-Toe) Board

        Game board object that holds the state of the game in progress.
        """
        return self._board_
    
    @property
    def draw_reward(self) -> float:
        """# (Draw) Reward (float)
        
        Reward yielded by ending game in a draw (neither player wins).
        """
        return self._draw_reward_
    
    @property
    def invalid_move_penalty(self) -> float:
        """# (Invalid Move) Penalty (float)
        
        Penalty incurred for attempting an invalid move.
        """
        return self._invalid_move_penalty_
    
    @property
    def loss_penalty(self) -> float:
        """# (Loss) Penalty (float)
        
        Penalty incurred by losing a game.
        """
        return self._loss_penalty_
    
    @property
    def move_penalty(self) -> float:
        """# (Move) Penalty (float)
        
        Cost of making a single move.
        """
        return self._move_penalty_
    
    @property
    def size(self) -> int:
        """# (Board) Size (int)
        
        Size of the Tic Tac Toe board.
        """
        return self._size_
    
    @property
    @override
    def state_space(self) -> int:
        """# State Space

        Size/dimension of tic-tac-toe board.
        """
        return self.size ** 2
    
    @property
    def win_reward(self) -> float:
        """# (Win) Reward (float)
        
        Reward yielded from winning a game.
        """
        return self._win_reward_
    
    # METHODS ======================================================================================
    
    @override
    def reset(self) -> None:
        """# Reset Environment.
        
        Resets the environment to its initial state, preparing it for a new game.
        """
        # Reset board.
        self._board_:   Board = Board(size = self.size)
        
    @override
    def step(self,
        action: Union[int, Tuple[int, int]]
    ) -> Tuple[ndarray, float, bool, Dict[str, Any]]:
        """# Step.

        ## Args:
            * action    (Union[int, Tuple[int, int]]):  Action submitted by agent.

        ## Returns:
            * Tuple[ndarray, float, bool, Dict[str, Any]]:
                * Resulting state of Tic-Tac-Toe board.
                * Reward yielded/penalty incurred by action.
                * Flag indicating if agent has reached a terminal state.
                * Metadata & statistics.
        """
        # Assert that action submitted is either integer or tuple.
        assert type(action) in [int, Tuple[int, int]], f"Action must be integer or coordinate, got {type(action)}"
        
        # Submit action based on type.
        move_is_valid:  bool =  self.board.enter_move_by_action(action = action)    \
                                if isinstance(action, int)                          \
                                else self.board.enter_move(action = action)
                                
        # If move was not valid, assign penalty.
        if not move_is_valid:               reward: float = self.invalid_move_penalty
        
        # Otherwise, if game is over..
        elif self.board.game_over:
            
            # If player won, assign reward.
            if self.board.winner == 1:      reward: float = self.win_reward
            
            # If opponent won, assign penalty.
            elif self.board.winner == -1:   reward: float = self.loss_penalty
            
            # If game was a draw, assign reward.
            elif self.board.is_draw:        reward: float = self.draw_reward
            
        # Otherwise, simply assign penalty for move, as game is still in progress.
        else:                               reward: float = self.move_penalty
        
        # Return results of action.
        return  (
                    # New state.
                    self.board.state,
                    
                    # Reward/Penalty
                    reward,
                    
                    # Terminated?
                    self.board.game_over,
                    
                    # Metadata/statistics.
                    self.board.statistics
                )
            
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Get Representation.
        
        Provide the string representation of the Tic-Tac-Toe board.

        ## Returns:
            * str:  String representation of the Tic-Tac-Toe board.
        """
        return self.board.__str__()
    
    def __str__(self) -> str:
        """# Get String.
        
        Provide the string representation of the Tic-Tac-Toe board.

        ## Returns:
            * str:  String representation of the Tic-Tac-Toe board.
        """
        return self.board.__str__()