"""# lucidium.agents.components.replay_buffer

Experience replay buffer for off-policy learning.
"""

__all__ = ["ExperienceReplayBuffer"]

from collections        import deque
from logging            import Logger
from random             import sample
from typing             import Any, Dict, Tuple

from torch              import FloatTensor, stack

from lucidium.utilities import get_child

class ExperienceReplayBuffer():
    """# Experience Replay Buffer
    
    An experience replay buffer is a data structure used in reinforcement learning to store and 
    sample past experiences (transitions) for training a deep neural network. This technique helps 
    stabilize training and improve sample efficiency by breaking correlations in the data.
    
    Adapted from: https://github.com/quantumiracle/Popular-RL-Algorithms/blob/master/sac.py
    """
    
    def __init__(self,
        capacity:   int =   1000000,
        batch_size: int =   128,
        to_device:  int =   "cpu"
    ):
        """# Instantiate Experience Replay Buffer.

        ## Args:
            * capacity      (int):  Maximum capacity of buffer. Defaults to 1,000,000.
            * batch_size    (int):  Size of training batches for sampling. Defaults to 128.
            * to_device     (str):  Device to use. Defaults to "cpu".
        """
        # Initialize logger.
        self.__logger__:    Logger =    get_child("reply-buffer")
        
        # Initialize buffer.
        self._buffer_:      deque =     deque(maxlen = capacity)
        
        # Define batch size.
        self._batch_size_:  int =       batch_size
        
        # Define device.
        self._device_:      str =       to_device
        
    # PROPERTIES ===================================================================================
    
    @property
    def read_for_training(self) -> bool:
        """# (Buffer is) Ready for Training?

        True if buffer contains enough transitions to create a training batch.
        """
        return len(self._buffer_) >= self._batch_size_
        
    # METHODS ======================================================================================
    
    def clear(self) -> None:
        """# Clear Buffer."""
        # Clear buffer.
        self._buffer_.clear()
        
        # Debug action.
        self.__logger__.debug(f"Experience replay buffer cleared.")
    
    def push(self,
        old_state:  Any,
        action:     Any,
        reward:     float,
        new_state:  Any,
        done:       bool
    ) -> None:
        """# Add Experience to Buffer.

        ## Args:
            * old_state (Any):      State before agent's action was submitted.
            * action    (Any):      Action submitted by agent.
            * reward    (float):    Reward yielded/penalty incurred by agent's action.
            * new_state (Any):      State of environment after agent's action was consumed.
            * done      (bool):     True if agent's action resulted in a terminal environment state.
        """
        # Assert that all transition components are provided.
        assert old_state is not None,   f"Old state not provided: {old_state}"
        assert action    is not None,   f"Action not provided: {action}"
        assert reward    is not None,   f"Reward not provided: {reward}"
        assert new_state is not None,   f"New state not provided: {new_state}"
        assert done      is not None,   f"Done not provided: {done}"

        # Append experience to buffer.
        self._buffer_.append((old_state, action, reward, new_state, done))
        
        # Debug action.
        self.__logger__.debug(f"Experience pushed: {old_state}, {action}, {reward}, {new_state}, {done}")
        
    def sample(self,
    ) -> Dict[str, FloatTensor]:
        """# Sample Buffer.

        ## Args:
            * batch_size    (int):  Number of experiences being sampled from buffer.

        ## Returns:
            * Mapping of transition components.
        """
        # Sample batch
        sampled_experiences = sample(self._buffer_, min(self._batch_size_, len(self._buffer_)))
        
        # Return stacked tensors
        return  {
                    "old_state":    stack([FloatTensor(exp[0]) for exp in sampled_experiences]).to(self._device_),
                    "action":       stack([FloatTensor(exp[1]) for exp in sampled_experiences]).to(self._device_),
                    "reward":       stack([FloatTensor([exp[2]]) for exp in sampled_experiences]).to(self._device_),
                    "new_state":    stack([FloatTensor(exp[3]) for exp in sampled_experiences]).to(self._device_),
                    "done":         stack([FloatTensor([float(exp[4])]) for exp in sampled_experiences]).to(self._device_)
                }
    
    # DUNDERS ======================================================================================
    
    def __len__(self) -> int:
        """# Current Length of Buffer"""
        return len(self._buffer_)