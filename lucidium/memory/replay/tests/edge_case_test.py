"""# lucidium.memory.replay.tests.edge_case_test

Test suite for edge cases pertaining to memory replay components.
"""

from typing                             import List

from numpy                              import array
from numpy.random                       import exponential, randint, randn
from numpy.typing                       import NDArray
from pytest                             import raises

from lucidium.memory.replay.core        import *
from lucidium.memory.replay.policy      import *
from lucidium.memory.replay.utilities   import SumTree

# NEGATIVE TESTS ===================================================================================

def test_invalid_policy() -> None:
    """# Test Invalid Policy for Buffer."""
    # Ensure error is reported when...
    with raises(ValueError, match = "Invalid sampling policy"):
        
        # Initializing buffer with invalid policy.
        ExperienceReplayBuffer(capacity = 1, policy = "invalid_policy")
        
def test_zero_capacity() -> None:
    """# Test Zero Capacity Initialization."""
    # Ensure error is reported when...
    with raises(ValueError, match = "Capacity expected to be positive integer"):
        
        # Initializing a sum tree with zero capacity.
        SumTree(capacity = 0)
        
    # Ensure error is reported when...
    with raises(ValueError, match = "Capacity expected to be positive integer"):
        
        # Initializing a buffer with zero capacity.
        ExperienceReplayBuffer(capacity = 0)
        
    # Ensure error is reported when...
    with raises(ValueError, match = "Capacity expected to be positive integer"):
        
        # Initializing uniform policy with zero capacity.
        UniformSampling(capacity = 0)
        
    # Ensure error is reported when...
    with raises(AssertionError, match = "Capacity must be greater than zero"):
        
        # Initializing prioritized policy with zero capacity.
        PrioritizedSampling(capacity = 0)
        
# UNCONVENTIONAL BUFFER CAPACITIES =================================================================

def test_very_small_buffer() -> None:
    """# Test Buffer with very Samll Capacity."""
    # Initialize buffer with capacity of 1.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 1, batch_size = 1)
    
    # Push single transition.
    buffer.push(array([1]), 0, 1.0, array([2]), False)
    
    # Sample from buffer.
    batch:  Batch =                     buffer.sample()
    
    # Ensure that proper batch was provided.
    assert len(batch.transitions) == 1, \
        f"Expected one transition sample from buffer, got {len(batch.transitions)}"
        
# EXTREME PRIORITIES ===============================================================================

def test_extreme_priorities() -> None:
    """# Test Extreme Priority Values."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 10, epsilon = 1e-8)
    
    # Add very small and very large priorities.
    policy.on_add(index = 0, priority = 1e6)
    policy.on_add(index = 1, priority = 1e-6)
    
    # Sample from policy.
    indices, weights = policy.sample(sample_range = 2, batch_size = 10)
    
    # Ensure that it still produces valid results.
    assert len(indices) == 10,                  \
        f"Expected 10 index samples, got {len(indices)}"
    assert len(weights) == 10,                  \
        f"Expected 10 weight samples, got {len(weights)}"
    assert all(0 <= w <= 1 for w in weights),   \
        f"Weights found to be oiutside of expected range [0, 1]"