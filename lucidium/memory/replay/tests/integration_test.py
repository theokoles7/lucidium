"""# lucidium.memory.replay.tests.integration_test

Test suite for integration of memory replay classes.
"""

from typing                                 import List

from numpy                                  import array
from numpy.random                           import exponential, randint, randn
from numpy.typing                           import NDArray

from lucidium.memory.replay.core.batch      import Batch
from lucidium.memory.replay.core.buffer     import ExperienceReplayBuffer
from lucidium.memory.replay.core.transition import Transition

# UNIFORM SAMPLING POLICY INTEGRATION ==============================================================

def test_uniform_policy_buffer_integration() -> None:
    """# Test Buffer Integration with Uniform Sampling Policy."""
    # Initialize buffer with uniform policy.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                            capacity =      100,
                                            batch_size =    10,
                                            policy =        "uniform"
                                        )
    
    # Simulate 50 transitions.
    for i in range(50):
        
        # Create dummy data.
        state:      NDArray =   randn(4)
        action:     int =       randint(0, 4)
        reward:     float =     randn()
        next_state: NDArray =   randn(4)
        done:       bool =      i % 10 == 9
        
        # Push dummy transition.
        buffer.push(state, action, reward, next_state, done)
        
    # Simulate 5 sample batches.
    for _ in range(5):
        
        # Sample from buffer.
        batch:  Batch = buffer.sample()
        
        # Ensure proper batch size.
        assert len(batch.transitions) == 10,    \
            f"Expected 10 transition samples, got {len(batch.transitions)}"
        assert len(batch.indices) == 10,        \
            f"Expected 10 index samples, got {len(batch.indices)}"
        assert batch.importance is None,           \
            f"Uniform policy should not produce weights, got {batch.importance}"
        
        # For each transition sampled...
        for t in batch.transitions:
            
            # Ensure they are valid.
            assert isinstance(t, Transition),   \
                f"Transition(s) found to be of improper type {type(t)}"
            assert t.state is not None,         \
                f"Transition state found to be None."
            assert t.next_state is not None,    \
                f"Transition next state found to be None."
                
# PRIORITIZED SAMPLING POLICY INTEGRATION ==========================================================

def test_prioritized_policy_buffer_integration() -> None:
    """# Test Buffer Integration with Prioritized Sampling Policy."""
    # Initialize buffer with uniform policy.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                            capacity =          100,
                                            batch_size =        10,
                                            policy =            "prioritized",
                                            alpha =             0.6,
                                            beta_start =        0.4,
                                            beta_end =          1.0,
                                            beta_anneal_steps = 1000
                                        )
    
    # Simulate 50 transitions.
    for i in range(50):
        
        # Create dummy data.
        state:      NDArray =   randn(4)
        action:     int =       randint(0, 4)
        reward:     float =     randn()
        next_state: NDArray =   randn(4)
        done:       bool =      i % 10 == 9
        
        # Push dummy transition.
        buffer.push(state, action, reward, next_state, done)
        
    # Simulate 10 sample batches.
    for _ in range(10):
        
        # Sample from buffer.
        batch:  Batch = buffer.sample()
        
        # Ensure proper batch size & weight range.
        assert len(batch.transitions) == 10,                \
            f"Expected 10 transition samples, got {len(batch.transitions)}"
        assert len(batch.indices) == 10,                    \
            f"Expected 10 index samples, got {len(batch.indices)}"
        assert all( 0 <= w <= 1 for w in batch.importance),    \
            f"Weights found to be outside of range [0, 1]"
            
        # Simulate temporal difference errors.
        td_errors:  NDArray =   exponential(scale = 1.0, size = 10)
        
        # Update priorities.
        buffer.update_priorities(indices = batch.indices, td_errors = td_errors)
        
        # Step for beta annealing.
        buffer.step()
        
        # For each transition sampled...
        for t in batch.transitions:
            
            # Ensure they are valid.
            assert isinstance(t, Transition),   \
                f"Transition(s) found to be of improper type {type(t)}"
            assert t.state is not None,         \
                f"Transition state found to be None."
            assert t.next_state is not None,    \
                f"Transition next state found to be None."
                
# BUFFER STRESS ====================================================================================

def test_buffer_capacity_stress() -> None:
    """# Test Buffer Capacity Stress."""
    # Initialize buffer
    buffer:     ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    5
                                            )
    
    # Simulate adding far more transitions that the buffer should hold.
    for i in range(100): buffer.push(array([i]), i, float(i), array([i + 1]), i % 20 == 19)
    
    # Ensure that buffer did not exceed capacity.
    assert buffer.size == 10,           \
        f"Buffer size {buffer.size} exceeded capacity {buffer.capacity}"
    
    # Ensure sampling is operational.
    batch:      Batch =                     buffer.sample()
    
    # Ensure proper sample size.
    assert len(batch.transitions) == 5, \
        f"Batch sample size expected to be 5, got {len(batch.transitions)}"
        
    # Gather actions from transition batch.
    actions:    List[int] =                 [t.action for t in batch.transitions]
    
    # Ensure that all actions are from recent transitions.
    assert all(a >= 90 for a in actions),   \
        f"Expected recent action data, got {actions}"