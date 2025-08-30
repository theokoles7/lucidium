"""# lucidium.memory.buffer

Standard experience replay buffer implementation.
"""

__all__ = ["ExperienceReplayBuffer"]

from collections                import deque
from logging                    import Logger
from random                     import sample
from typing                     import Iterator, List, Optional

from lucidium.memory.transition import Transition
from lucidium.utilities         import get_child

class ExperienceReplayBuffer():
    """# Experience Replay Buffer.
    
    Cyclic buffer of bounded size that holds transitions observed [recently] by an agent.
    """
    
    def __init__(self,
        capacity:   int =   1e6,
        batch_size: int =   128
    ):
        """# Instantiate Experience Replay Bufer.

        ## Args:
            * capacity      (int):  Maximum capacity of buffer. Defaults to 1_000_000.
            * batch_size    (int):  Size of batches that will be sampled from buffer. Defaults to 
                                    128.
        """
        # Initialize logger.
        self.__logger__:    Logger =    get_child("replay-buffer")
        
        # Initialize buffer.
        self._buffer_:      deque =     deque(maxlen = int(capacity))
        
        # Define properties.
        self._capacity_:    int =       capacity
        self._batch_size_:  int =       batch_size
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized experience replay buffer ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @property
    def batch_size(self) -> int:
        """# Sampling Batch Size
        
        Size of batches that will be sampled from buffer.
        """
        return self._batch_size_
    
    @property
    def capacity(self) -> int:
        """# Buffer Capacity.

        Maximum capacity of buffer.
        """
        return self._capacity_
    
    @property
    def is_ready_for_sampling(self) -> bool:
        """# (Buffer) is Ready for Sampling?
        
        True if buffer contains at least `batch_size` transitions.
        """
        return self.size >= self.batch_size
    
    @property
    def size(self) -> int:
        """# Current Buffer Size"""
        return len(self._buffer_)
    
    # METHODS ======================================================================================
    
    def clear(self) -> None:
        """# Clear Buffer.
        
        Clear all current transitions from buffer.
        """
        self._buffer_.clear()
        
    def push(self, *args) -> None:
        """# Push Transition to Buffer.

        ## Args:
            * old_state:    Environment state prior to agent's action.
            * action:       Action submitted by agent.
            * reward:       Reward yielded/penalty incurred by agent's action.
            * new_state:    Environment state after agent submitted action.
            * done:         Flag to indicate if new state is terminal.
        """
        self._buffer_.append(Transition(*args))
        
    def sample(self,
        batch_size: Optional[int] = None
    ) -> List[Transition]:
        """# Sample Transitions.

        ## Args:
            * batch_size (int): Quantity of transition samples. Defaults to batch size defined on 
                                initialization.

        ## Returns:
            * List[Transition]: Transition samples.
        """
        return sample(self._buffer_, self.batch_size if batch_size is None else batch_size)
        
    # DUNDERS ======================================================================================
    
    def __iter__(self) -> Iterator:
        """# Experience Replay Buffer Iterable"""
        return self._buffer_.copy().__iter__()
    
    def __len__(self) -> int:
        """# Current Buffer Size"""
        return self.size
    
    def __repr__(self) -> str:
        """# Experience Replay Buffer Object Representation."""
        return f"""<ExperienceReplayBuffer(size = {self.size}, capacity = {self.capacity})>"""
    
    def __str__(self) -> str:
        """# Experience Replay Buffer String Representation."""
        return f"""<ExperienceReplayBuffer(size = {self.size}, capacity = {self.capacity})>"""