"""# lucidium.memory.replay.core.tests.buffer._test

Experience replay buffer test suite.
"""

from typing                                 import List

from numpy                                  import array
from numpy.typing                           import NDArray
from pytest                                 import raises

from lucidium.memory.replay.core.batch      import Batch
from lucidium.memory.replay.core.buffer     import ExperienceReplayBuffer
from lucidium.memory.replay.core.transition import Transition

# INITIALIZATION ===================================================================================

def test_buffer_init_default() -> None:
    """# Test Default Buffer Initialization."""
    # Initialize a buffer with no arguments.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer()
    
    # Validate default properties.
    assert buffer.capacity == 1000000,  \
        f"Buffer capacity expected to be 1,000,000, got {buffer.capacity}"
    assert buffer.batch_size == 128,    \
        f"Buffer batch size expected to be 128, got {buffer.batch_size}"
    assert buffer.size == 0,            \
        f"Buffer capacity expected to be 0, got {buffer.size}"
        
def test_buffer_init_custom() -> None:
    """# Test Custom Buffer Initialization."""
    # Initialize a buffer with arguments.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                            capacity =      1000,
                                            batch_size =    64,
                                            policy =        "prioritized",
                                            alpha =         0.8
                                        )
    
    # Validate properties.
    assert buffer.capacity == 1000,             \
        f"Buffer capacity expected to be 1,000, got {buffer.capacity}"
    assert buffer.batch_size == 64,             \
        f"Buffer batch size expected to be 64, got {buffer.batch_size}"
    assert not buffer.is_ready_for_sampling,    \
        f"Buffer with capacity = 64 should not be ready for sampling upon initialization."
        
# PUSHING ==========================================================================================

def test_push_single() -> None:
    """# Test Pushing a Single Transition to Buffer."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 10)

    # Define transition parameters.
    state:      NDArray =       array([1, 2, 3])
    action:     int =           0
    reward:     float =         1.0
    next_state: NDArray =       array([2, 3, 4])
    done:       bool =          False
    
    # Push transition.
    index:      int =           buffer.push(state, action, reward, next_state, done)
    
    # Validate state of buffer after push.
    assert index == 0,                  \
        f"Index of first transition pushed expected to be zero, got {index}"
    assert buffer.size == 1,            \
        f"Buffer size expected to be 1, got {buffer.size}"
    assert buffer[index] is not None,   \
        f"Transition that was pushed could not be found in buffer"
        
def test_push_multiple() -> None:
    """# Test Pushing Multiple Transitions to Buffer."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 10)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Ensure buffer contains exactly 3 transitions.
    assert buffer.size == 3, f"Buffer size expected to be 3, got {buffer.size}"
    
def test_circular_overwrite() -> None:
    """# Test Circular Overwrite Functionality."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 3)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Ensure buffer contains exactly 3 transitions.
    assert buffer.size == 3, f"Buffer size expected to be 3, got {buffer.size}"
    
    # Push one more transition to cause a circular overwrite.
    index:  int =   buffer.push(array([3]), 3, float(3), array([4]), False)
    
    # Validate state of buffer after circular overwrite.
    assert index == 0,                  \
        f"Index of last push expected to be zero, got {index}"
    assert buffer.size == 3,            \
        f"Buffer size expected to remain at 3, got {buffer.size}"
    assert buffer[index].action == 3,   \
        f"Last transition action expected to be 3, got {buffer[index].action}"
        
# SAMPLING =========================================================================================

def test_ready_for_sampling() -> None:
    """# Test Condition where Buffer is Ready for Sampling."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Ensure that buffer is ready for sampling.
    assert buffer.is_ready_for_sampling,    \
        f"Buffer with capacity = 3 should be ready for sampling after 3 transitions."
        
    # Sample from buffer.
    batch:  Batch = buffer.sample()
    
    # Validate transitions & indices.
    assert len(batch.transitions) == 3,      \
        f"Length of transitions from sample expected to be 3, got {len(batch.transitions)}"
    assert len(batch.indices) == 3,         \
        f"Length of indices from sample expected to be 3, got {len(batch.indices)}"
        
def test_not_ready_for_sampling() -> None:
    """# Test Condition where Buffer is not Ready for Sampling."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Push 2 transitions to buffer.
    for i in range(2): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Ensure that buffer is not ready for sampling.
    assert not buffer.is_ready_for_sampling,    \
        f"Buffer with capacity = 3 should not be ready for sampling after 2 transitions."
        
    # Ensure that attempting to sample raises an error.
    with raises(RuntimeError): buffer.sample()
    
def test_sample_custom_batch_size() -> None:
    """# Test Sampling a Custom Batch Size."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Sample only two transitions from buffer.
    batch:  Batch = buffer.sample(batch_size = 2)
    
    # Validate transitions & indices.
    assert len(batch.transitions) == 2,      \
        f"Length of transitions from sample expected to be 2, got {len(batch.transitions)}"
    assert len(batch.indices) == 2,         \
        f"Length of indices from sample expected to be 2, got {len(batch.indices)}"
        
# CLEARING =========================================================================================

def test_clearing_the_buffer() -> None:
    """# Test Clearing the Buffer."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Ensure pre-condition (buffer containing transitions).
    assert buffer.size == 3, f"Buffer expected to contain 3 transitions, got {buffer.size}"
    
    # Clear the buffer.
    buffer.clear()
    
    # Ensure post-condition (buffer containing no transitions).
    assert buffer.size == 0, f"Buffer expected to contain 0 transitions, got {buffer.size}"
    
# STEPPING =========================================================================================

def test_buffer_step() -> None:
    """# Test Buffer Step."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Simply ensure that no exceptions are raised, as detailed testing for this method will be 
    # policy-specific.
    buffer.step()
    
# ITERATION ========================================================================================

def test_buffer_iteration() -> None:
    """# Test Buffer Iteration."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Convert buffer to list of transitions.
    transitions:    List[Transition] =  list(buffer)
    
    # Ensure there are 5 transitions (and that 2 of them are None).
    assert len(transitions) == 5,                               \
        f"Length of transitions expected to be 5, got {len(transitions)}"
    assert sum(1 for t in transitions if t is not None) == 3,   \
        f"Quantity of transitions expected to be 3, got "       \
        f"{sum(1 for t in transitions if t is not None)}"
        
def test_buffer_length() -> None:
    """# Test Buffer Length Property."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity = 5, batch_size = 3)
    
    assert len(buffer) == 0,    \
        f"Length of buffer before transitions expected to be 0, got {len(buffer)}"
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    assert len(buffer) == 3,    \
        f"Length of buffer after 3 transitions expected to be 3, got {len(buffer)}"
        
# PRIORITIES =======================================================================================

def test_priority_update() -> None:
    """# Test Updating Priorities."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(policy = "prioritized")
    
    # Push 3 transitions to buffer.
    for i in range(3): buffer.push(array([i]), i, float(i), array([i + 1]), False)
    
    # Update priorities.
    buffer.update_priorities([0, 1], [1.0, 2.0])
    
# REPRESENTATION ===================================================================================
    
def test_buffer_repr():
    """Test Buffer String representations."""
    # Initialize buffer.
    buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(capacity=10)
    
    # Get object & string representations.
    object_representation:  str =   repr(buffer)
    string_representation:  str =   str(buffer)
    
    assert "ExperienceReplayBuffer" in object_representation,   \
        f"Buffer object representation malformed: {repr(buffer)}"
    assert "size = 0" in object_representation,                 \
        f"Buffer object representation malformed: {repr(buffer)}"
    assert "capacity = 10" in object_representation,            \
        f"Buffer object representation malformed: {repr(buffer)}"
    assert object_representation == string_representation,      \
        f"Buffer string representation malformed: {str(buffer)}"