"""# lucidium.memory.replay.policy.prioritized

Prioritized experience replay sampling policy implementation.
"""

__all__ = ["PrioritizedSampling"]

from random                                     import randrange, uniform
from typing                                     import Iterable, List, Optional, Tuple

from numpy                                      import asarray, float32, int32, ones, zeros
from numpy.random                               import randint
from numpy.typing                               import NDArray

from lucidium.memory.replay.policy.protocol     import SamplingPolicy
from lucidium.memory.replay.utilities.sum_tree  import SumTree

class PrioritizedSampling(SamplingPolicy):
    r"""# :class:`PrioritizedSampling`

    Proportional Prioritized Experience Replay (Schaul et al., 2016).
    
    * Sampling probability P(i) = p_i / sum(p)
    * p_i is (|δ_i| + eps)^alpha, stored directly (already ^alpha) in the tree
    * Importance-sampling: w_i = (N * P(i))^-beta, normalized by max weight to [0,1]
    * β is annealed from beta_start to beta_end over beta_anneal_steps via step()
    """
    
    def __init__(self,
        capacity:           int,
        alpha:              float = 0.6,
        beta_start:         float = 0.4,
        beta_end:           float = 1.0,
        beta_anneal_steps:  int =   200000,
        epsilon:            float = 1e-6,
        initial_priority:   float = 1.0
    ):
        r"""# Instantiate Prioritized Sampling Policy.
        
        ## Args:
            * :param:`capacity`             (int):      Maximum number of transitions the buffer 
                                                        can store.
            * :param:`alpha`                (float):    Degree of prioritization (0 = uniform, 1 = 
                                                        full PER).
            * :param:`beta_start`           (float):    Initial beta value for importance-sampling 
                                                        correction.
            * :param:`beta_end`             (float):    Final beta value to anneal toward (often 
                                                        1.0).
            * :param:`beta_anneal_steps`    (int):      Number of calls to `step()` before beta 
                                                        reaches `beta_end`.
            * :param:`epsilon`              (float):    Small constant to avoid zero probabilites.
            * :param:`initial_priority`     (float):    Default priority value assigned to new 
                                                        transitions (ensures they are able to be 
                                                        sampled soon after insertion).
        """
        # Validate arguments.
        assert alpha >= 0.0,                f"Alpha parameter must be >= 0, got {alpha}"
        assert 0.0 <= beta_start <= 1.0,    f"Beta start must be in range [0.0, 1.0], got {beta_start}"
        assert 0.0 <= beta_end <= 1.0,      f"Beta end must be in range [0.0, 1.0], got {beta_end}"
        
        # Define hyperparameters.
        self._capacity_:            int =       int(capacity)
        self._alpha_:               float =     float(alpha)
        self._beta_:                float =     float(beta_start)
        self._beta_start_:          float =     float(beta_start)
        self._beta_end_:            float =     float(beta_end)
        self._beta_anneal_steps_:   int =       max(1, int(beta_anneal_steps))
        self._anneal_step_:         int =       0
        self._epsilon_:             float =     float(epsilon)
        self._initial_priority_:    float =     float(initial_priority)
        
        # Initialize segment tree to support O(log N) sampling/updates.
        self._tree_:                SumTree =   SumTree(capacity = self._capacity_)
        
        # Initialize array to track priorities.
        self._priorities_:          NDArray =   zeros(self._capacity_, dtype = float32)
        
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
        # Determine priority assignment, in case one is not provided.
        base:       float =         self._initial_priority_ if priority is None else float(priority)
        
        # Normalize priority.
        priority:   float =         (abs(base) + self._epsilon_) ** self._alpha_
        
        # Update priorities table.
        self._priorities_[index] =  priority
        
        # Update tree.
        self._tree_.update(index, priority)
    
    def reset(self,
        capacity:   int
    ) -> None:
        r"""# Reset.
        
        Invoked on at buffer construction and again when the buffer is cleared. Implementations 
        should allocate internal data structures sized to `capacity`.
        
        ## Args:
            * :param:`capacity` (int):  Maximum number of transitions the buffer can store.
        """
        self.__init__(
            capacity =          capacity,
            alpha =             self._alpha_,
            beta_start =        self._beta_start_,
            beta_end =          self._beta_end_,
            beta_anneal_steps = self._beta_anneal_steps_,
            epsilon =           self._epsilon_,
            initial_priority =  self._initial_priority_,
        )
    
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
        # Buffer cannot be sampled if it's empty.
        if range <= 0: raise ValueError("Cannot sample from an empty buffer.")
        
        # Extract total sum of current priorities.
        priority_sum:   float =     self._tree_.total
        
        # If sum is zero or less...
        if priority_sum <= 0.0:
            
            # Fall back to uniform sampling, as priorities are degenerate.
            return  randint(0, range, size = batch_size, dtype = int32),\
                    ones(batch_size, dtype = float32)
            
        # Otherwise, determine segment size.
        segment:        float =     priority_sum / batch_size
        
        # Initialize list of sample indices.
        samples:        List[int] = []
        
        # For each index needed...
        for i in range(batch_size):
            
            # Compute the start of the stratified segment in the [0, priority_sum] interval.
            a:      float = segment * i
            
            # Compute the end of the stratified segment.
            b:      float = segment * (i + 1)
            
            # Pick a random mass inside of this segment (uniformly). This ensures the coverage of 
            # the entire [0, priority_sum] interval while reducing variance compared to drawing all 
            # samples independently.
            mass:   float = uniform(a, b)
            
            # Traverse the sum-tree to find the index of the leaf whose cumulative priority contains 
            # this mass. This effectively samples an index proportional to its priority.
            index:  int =   self._tree_.find_prefix_sum_index(mass = mass)
            
            # During buffer warmup, valid_range < capacity (not all slots are filled). The sum-tree 
            # always covers full capacity, so we clamp indices that fall outside of the valid range 
            # by resampling uniformly with [0, valid_range).
            if index >= range: index = randrange(range)
            
            # Append the chosen index to the sample list.
            samples.append(index)
            
        # Convert sampled indices to numpy array.
        indices:    NDArray =   asarray(samples, dtype = int32)
        
        # Gather priorities of sampled indices.
        p_i:        NDArray =   self._priorities_[indices]
        
        # Convert priorities to probabilities by dividing by total mass.
        P_i:        NDArray =   p_i / (priority_sum + self._epsilon_)
        
        # Generate importance weights.
        weights:    NDArray =   (float(range) * P_i) ** (-self._beta_)
        
        # Extract minimum priority.
        min_p:      float =     max(self._tree_.minimum, self._epsilon_)
        
        # Compute minimum priority over all leaves.
        min_P:      float =     min_p / (priority_sum + self._epsilon_)
        
        # Compute the maximum possible importance-sampling weight.
        max_w:      float =     (float(range) * min_P) ** (-self._beta_)
        
        # Normalize weights.
        weights:    NDArray =   (weights / (max_w + self._epsilon_)).astype(float32)
        
        # Provide samples indices and weights.
        return indices, weights
    
    def step(self) -> None:
        r"""# Step.
        
        Typical use cases include annealing β in prioritized replay or updating 
        exploration/exploitation balances in custom strategies. Called once per learner update. 
        No-op for policies that require no scheduling.
        """
        # If beta is not completely annealed...
        if self._beta_ < self._beta_end_:
            
            # Determine anneal step.
            self._anneal_step_: int =   min(self._anneal_step_ + 1, self._beta_anneal_steps_)
            
            # Compute time interval.
            t:                  float = self._anneal_step_ / self._beta_anneal_steps_
            
            # Anneal beta.
            self._beta_:        float = (1.0 - t) * self._beta_start_ + t * self._beta_end_
    
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
        # For each sample provided...
        for index, td_error in zip(indices, td_errors):
            
            # Ensure index is integer.
            index:      int =   int(index)
            
            # Compute priority update.
            priority:   float = (abs(float(td_error)) + self._epsilon_) ** self._alpha_
            
            # Update priorty table.
            self._priorities_[index] = priority
            
            # Update sum tree.
            self._tree_.update(index, priority)