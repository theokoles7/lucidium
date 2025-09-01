"""# lucidium.memory.replay.policy.protocol

Generic implementation of experience replay policy protocol.
"""

__all__ = ["SamplingPolicy"]

from typing         import Iterable, Optional, Protocol, runtime_checkable, Tuple

from numpy.typing   import NDArray

@runtime_checkable
class SamplingPolicy(Protocol):
    r"""# :class:`SamplingPolicy`
    
    Strategy interface that dictates how to sample from an experience replay buffer.
    
    ## Methods:
    * :meth:`on_add`:               Notify the policy that a new transitions has been added.
    * :meth:`reset`:                Reset the policy state for a given buffer capacity.
    * :meth:`sample`:               Sample a batch of indices (and optional IS weights).
    * :meth:`step`:                 Advance any internal schedules by one learner step.
    * :meth:`update_priorities`:    Update per-transition priorities after a learning step.
    """
    
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
        ...
    
    def reset(self,
        capacity:   int
    ) -> None:
        r"""# Reset.
        
        Invoked on at buffer construction and again when the buffer is cleared. Implementations 
        should allocate internal data structures sized to `capacity`.
        
        ## Args:
            * :param:`capacity` (int):  Maximum number of transitions the buffer can store.
        """
        ...
    
    def sample(self,
        range:      int,
        batch_size: int
    ) -> Tuple[NDArray, Optional[NDArray]]:
        r"""# Sample.
        
        Sample a batch of indices and priority weights.
        
        ## Args:
            * :param:`range`    (int):      Current number of valid transitions in the buffer 
                                            (i.e., `len(buffer)`).
            * :param:`batch_size`   (int):  Number of samples to draw.
            
        ## Returns:
            * `indices`:    Numpy array of integers of shape ``[batch_size]`` containing buffer 
                            indices in the range ``[0, range)``.
            * `weights`:    Numpy array of floats of shape ``[batch_size]`` containing per-sample 
                            importance-sampling weights in ``[0, 1]``.
        """
        ...
    
    def step(self) -> None:
        r"""# Step.
        
        Typical use cases include annealing β in prioritized replay or updating 
        exploration/exploitation balances in custom strategies. Called once per learner update. 
        No-op for policies that require no scheduling.
        """
        ...
    
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
        ...