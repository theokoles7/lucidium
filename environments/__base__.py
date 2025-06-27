"""# lucidium.environments.base

This module provides the base class for all environments in the Lucidium framework.
"""

__all__ = ["Environment"]

from abc        import ABC, abstractmethod
from logging    import Logger
from typing     import Any, Dict, Tuple

class Environment(ABC):
    """Abstract Environment Class
    
    This class defines the base structure for an environment that can be interacted with by agents.
    
    ## Properties:
        * action_space  (Any):  Actions possible within the environment.
        * state_space   (Any):  Quantification of possible states in which the environment can be 
                                observed.
    """
    
    def __init__(self, **kwargs):
        """Initialize base Environment object."""
        # Declare logger member.
        self.__logger__:        Logger
        
        # Declare attributes and their types.
        self._action_space_:    Any
        self._state_space_:     Any
        
    # PROPERTIES ===================================================================================
    
    @property
    @abstractmethod
    def action_space(self) -> Any:
        """# Action Space (Any)
        
        This property should return the actions possible within the environment.
        """
        pass
    
    @property
    @abstractmethod
    def state_space(self) -> Any:
        """# State Space (Any)
        
        This property should return the quantification of possible states in which the environment 
        can be observed.
        """
        pass
    
    # METHODS ======================================================================================
    
    @abstractmethod
    def reset(self) -> Any:
        """# Reset Environment.
        
        This method should reset the environment to its initial state and return the initial state.
        
        ## Returns:
            * Any:  Initial state of the environment.
        """
        pass
    
    @abstractmethod
    def step(self,
        action: Any
    ) -> Tuple[Any, float, bool, Dict]:
        """# Step.

        The second critical step in the reinforcement learning loop.

        Applies the agent's action, updates the environment state, and returns the resulting new 
        state, reward, done flag, and optional metadata.
        
        ## Args:
            * action    (Any):  Action to be taken in the environment.
        
        ## Returns:
            * Tuple[Any, float, bool, Dict]:
                - Any:      Next state of the environment
                - float:    Reward received
                - bool:     Done flag indicating if the episode has ended
                - Dict:     Additional information
        """
        pass