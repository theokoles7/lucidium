"""# lucidium.memory.replay.policy.uniform

Uniform experience replay sampling policy implementation.
"""

__all__ = ["UniformSampling"]

from typing                                 import Iterable, Optional, Tuple

from numpy                                  import int32
from numpy.random                           import randint
from numpy.typing                           import NDArray

from lucidium.memory.replay.policy.protocol import SamplingPolicy

class UniformSampling(SamplingPolicy):
    r"""# :class:`UniformSampling`

    Uniform (vanilla) sampling policy for experience replay.
    """
    
    def __init__(self,
        capacity:   int
    ):
        r"""# Instantiate Unfirom Sampling Policy.
        
        ## Args:
            * :param:`capacity` (int):  Maximum number of transitions the buffer can store.
        """
        # Ensure that capacity is positive.
        if capacity <= 0: raise ValueError(f"Capacity expected to be positive integer, got {capacity}")
        
        # Define properties.
        self._capacity_:    int =   int(capacity)
        
    # PROPERTIES ===================================================================================
    
    @property
    def capacity(self) -> int:
        """# Policy Capacity."""
        return self._capacity_
        
    # METHODS ======================================================================================
    
    def on_add(self,
        index:      int,
        priority:   Optional[float] =   None
    ) -> None:
        r"""# On Add.
        
        Called every time the buffer inserts or overwrites a transition at slot `index`. 
        Implementations may use this to initialize or update metadata (e.g., assign an initial 
        priority to the transition memory).

        ## Args:
            * :param:`index`    (int):      Position in the replay buffer that was just written.
            * :param:`priority` (float):    Transition's priority hint (e.g., an initial TD error). 
                                            If not provided, the policy should fall back to a 
                                            default scheme.
        """
        # Nothing to track in a uniform policy.
        return
    
    def reset(self,
        capacity:   int
    ) -> None:
        r"""# Reset.
        
        Invoked on at buffer construction and again when the buffer is cleared. Implementations 
        should allocate internal data structures sized to `capacity`.
        
        ## Args:
            * :param:`capacity` (int):  Maximum number of transitions the buffer can store.
        """
        self._capacity_:    int =   capacity
    
    def sample(self,
        sample_range:   int,
        batch_size:     int
    ) -> Tuple[NDArray, Optional[NDArray]]:
        r"""# Sample.
        
        Sample a batch of indices and priority weights.
        
        ## Args:
            * :param:`sample_range` (int):      Current number of valid transitions in the buffer 
                                            (i.e., `len(buffer)`).
            * :param:`batch_size`   (int):  Number of samples to draw.
            
        ## Returns:
            * `indices`:    Numpy array of integers of shape ``[batch_size]`` containing buffer 
                            indices in the range ``[0, range)``.
            * `weights`:    Numpy array of floats of shape ``[batch_size]`` containing per-sample 
                            importance-sampling weights in ``[0, 1]``.
        """
        # Buffer cannot be sampled if it's empty.
        if sample_range <= 0: raise RuntimeError("Cannot sample from an empty buffer.")
        
        # Return sampling indices.
        return randint(0, sample_range, size = batch_size, dtype = int32), None
    
    def step(self) -> None:
        r"""# Step.
        
        Typical use cases include annealing β in prioritized replay or updating 
        exploration/exploitation balances in custom strategies. Called once per learner update. 
        No-op for policies that require no scheduling.
        """
        # No schedules to run for uniform policy.
        return
    
    def update_priorities(self,
        indices:    Iterable[int],
        td_errors:  Iterable[float]
    ) -> None:
        r"""# Update Priorities.
        
        For policies like Prioritized Experience Replay (PER), this method allows the buffer to 
        refresh priorities with new TD errors after backpropagation.

        ## Args:
            * :param:`indices`      (Iterable[int]):    Iterable of buffer indices that were 
                                                        sampled and used in the learner update.
            * :param:`td_errors`    (Iterable[float]):  Iterable of TD error magnitudes (same 
                                                        length as ``indices``). Each error 
                                                        corresponds to the transition at the same 
                                                        position in ``indices``.
        """
        # No priorities tracked in uniform policy.
        return