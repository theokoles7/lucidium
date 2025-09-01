"""# lucidium.memory.replay.core.buffer

Standard experience replay buffer implementation.
"""

__all__ = ["ExperienceReplayBuffer"]

from logging                                import Logger
from random                                 import sample
from typing                                 import Any, Iterable, Iterator, List, Literal, Optional, Tuple

from numpy.typing                           import NDArray

from lucidium.memory.replay.core.transition import Transition
from lucidium.memory.replay.policy          import *
from lucidium.utilities                     import get_child

class ExperienceReplayBuffer():
    """# Experience Replay Buffer.
    
    Cyclic buffer of bounded size that holds transitions observed [recently] by an agent.
    """
    
    def __init__(self,
        capacity:           int =                               1e6,
        batch_size:         int =                               128,
        policy:             Literal["prioritized", "uniform"] = "uniform",
        **policy_kwargs:    Any
    ):
        """# Instantiate Experience Replay Bufer.

        ## Args:
        * :param:`capacity`     (int):  Maximum capacity of buffer. Defaults to 1_000_000.
        * :param:`batch_size`   (int):  Size of batches that will be sampled from buffer. Defaults 
                                        to 128.
        * :param:`policy`       (str):  Policy to dictate sampling strategy.
        
        ## Prioritized Policy Args:
        * :param:`capacity`             (int):      Maximum number of transitions the buffer can 
                                                    store.
        * :param:`alpha`                (float):    Degree of prioritization (0 = uniform, 1 = full 
                                                    PER).
        * :param:`beta_start`           (float):    Initial beta value for importance-sampling 
                                                    correction.
        * :param:`beta_end`             (float):    Final beta value to anneal toward (often 1.0).
        * :param:`beta_anneal_steps`    (int):      Number of calls to `step()` before beta reaches 
                                                    `beta_end`.
        * :param:`epsilon`              (float):    Small constant to avoid zero probabilites.
        * :param:`initial_priority`     (float):    Default priority value assigned to new 
                                                    transitions (ensures they are able to be sampled 
                                                    soon after insertion).
        """
        # Initialize logger.
        self.__logger__:    Logger =                        get_child("replay-buffer")
        
        # Define properties.
        self._capacity_:    int =                           int(capacity)
        self._batch_size_:  int =                           int(batch_size)
        
        # Initialize buffer.
        self._buffer_:      List[Optional[Transition]] =    [None] * self._capacity_
        self._head_:        int =                           0
        self._size_:        int =                           0
        
        # Set sampling policy.
        self._set_policy_(policy = policy, **policy_kwargs)
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized {self.__repr__()}")
        
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
        return self._size_
    
    # METHODS ======================================================================================
    
    def clear(self) -> None:
        """# Clear Buffer.
        
        Clear all current transitions from buffer.
        """
        # Reinitialize buffer.
        self._buffer_:  List[Optional[Transition]] =    [None] * self._capacity_
        self._head_:    int =                           0
        self._size_:    int =                           0
        
        # Reset policy.
        self._policy_.reset(capacity = self._capacity_)
        
    def push(self, *args) -> int:
        """# Push Transition to Buffer.

        ## Args:
        * :param:`old_state`:   Environment state prior to agent's action.
        * :param:`action`:      Action submitted by agent.
        * :param:`reward`:      Reward yielded/penalty incurred by agent's action.
        * :param:`new_state`:   Environment state after agent submitted action.
        * :param:`done`:        Flag to indicate if new state is terminal.
            
        ## Returns:
        * int:  Index of transition written to buffer.
        """
        # Record current index.
        index:  int =   self._head_
        
        # Write transition to buffer.
        self._buffer_[index] =  Transition(*args)
        
        # Advance head.
        self._head_:    int =   (self._head_ + 1) % self._capacity_
        self._size_:    int =   min(self._size_ + 1, self._capacity_)
        
        # Notify policy.
        self._policy_.on_add(index = index, priority = None)
        
        # Return index of transition written.
        return index
        
    def sample(self,
        batch_size: Optional[int] = None
    ) -> Tuple[List[Transition], NDArray, Optional[NDArray]]:
        """# Sample Transitions.

        ## Args:
            * batch_size (int): Quantity of transition samples. Defaults to batch size defined on 
                                initialization.

        ## Returns:
        * transitions   (List[Transition]): Transition samples.
        * indices       (NDArray):          Array of sample indices.
        * weights       (NDArray | None):   Priority weights.
        """
        # Report error if buffer is empty.
        if self._size_ == 0: raise ValueError("Cannot sample from an empty buffer.")
        
        # Determine batch size.
        B:              int =               self._batch_size_ if batch_size is None else int(batch_size)
        
        # Delegate index selection to policy.
        indices, weights =  self._policy_.sample(range = self._size_, batch_size = B)
        
        # Initialize list of transition samples.
        transitions:    List[Transition] =  []
        
        # Extract transition samples.
        for i in indices: transitions.append(self._buffer_[int(i)])
        
        # Return transition samples and their priority weights.
        return transitions, indices, weights
    
    def step(self) -> None:
        """# Step.
        
        Advance policy schedules by one learner step.
        """
        self._policy_.step()
        
    def update_priorities(self,
        indices:    Iterable[int],
        td_errors:  Iterable[float]
    ) -> None:
        """# Update Priorities.
        
        Update priorities after a learner step.
        """
        self._policy_.update_priorities(indices = indices, td_errors = td_errors)
    
    # HELPERS ======================================================================================
    
    def _set_policy_(self,
        policy: Literal["prioritized", "uniform"],
        **kwargs
    ) -> None:
        """# Set Sampling Policy."""
        # Define policy details.
        self._policy_name_: str =   policy
        
        # Match policy.
        match policy:
            
            case "prioritized": self._policy_:  PrioritizedSampling =   PrioritizedSampling(
                                                                            capacity =  self._capacity_,
                                                                            **kwargs
                                                                        )
            
            case "uniform":     self._policy_:  UniformSampling =       UniformSampling(
                                                                            capacity =  self._capacity_
                                                                        )
            
            case _:             raise ValueError(f"Invalid sampling policy provided: {policy}")
            
        # Initialize policy.
        self._policy_.reset(capacity = self._capacity_)
        
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