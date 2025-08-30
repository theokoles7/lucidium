"""# lucidium.memory.tests.test_buffer

Test suite for Experience Replay Buffer.
"""

from lucidium.memory.buffer     import ExperienceReplayBuffer

class TestExperienceReplayBuffer():
    """# Experience Replay Buffer Test Suite."""
        
    def test_buffer_add_and_size(self):
        """# Test Adding Transitions and Size Tracking in Experience Replay Buffer."""
        # Initialize buffer.
        buffer:     ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                    capacity =      10,
                                                    batch_size =    4
                                                )
        
        # For multipleiterations...
        for i in range(15):
            
            # Add transition.
            buffer.push([0, 0], 0, 0.0, [0, 1], False)
            
            # Calculate expected size (capped at capacity).
            expected_size: int = min(i + 1, buffer.capacity)
            
            # Verify size.
            assert buffer.size == expected_size, f"Buffer size expected to be {expected_size}, got {buffer.size}"
            
    def test_buffer_clear(self):
        """# Test Clearing of Experience Replay Buffer."""
        # Initialize buffer and add transitions.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer()
        
        # Push 10 transitions.
        for _ in range(10): buffer.push([0, 0], 0, 0.0, [0, 1], False)
        
        # Verify size before clearing.
        assert buffer.size                  == 10,      f"Buffer size expected to be 10 before clearing"
        
        # Clear buffer.
        buffer.clear()
        
        # Verify clearing.
        assert buffer.size                  == 0,       f"Buffer size expected to be 0 after clearing, got {buffer.size}"
        assert buffer.is_ready_for_sampling == False,    "Buffer should not be ready for sampling after clearing"
        
    def test_buffer_initialization_custom(self):
        """# Test Custom Initialization of Experience Replay Buffer."""
        # Define custom parameters.
        custom_capacity:    int =   500_000
        custom_batch_size:  int =   64
        
        # Initialize buffer with custom parameters.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      custom_capacity,
                                                batch_size =    custom_batch_size
                                            )
        
        # Verify initialization.
        assert buffer.capacity              == custom_capacity,     f"Buffer capacity expected to be {custom_capacity}, got {buffer.capacity}"
        assert buffer.batch_size            == custom_batch_size,   f"Buffer batch size expected to be {custom_batch_size}, got {buffer.batch_size}"
        assert buffer.size                  == 0,                   f"Buffer size expected to be 0 upon initialization, got {buffer.size}"
        assert buffer.is_ready_for_sampling == False,                "Buffer should not be ready for sampling upon initialization"
    
    def test_buffer_initialization_defaults(self):
        """# Test Initialization of Experience Replay Buffer."""
        # Initialize buffer.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer()
        
        # Verify initialization.
        assert buffer.capacity              == 1000000, f"Buffer capacity expected to be 500_000, got {buffer.capacity}"
        assert buffer.batch_size            == 128,     f"Buffer batch size expected to be 64, got {buffer.batch_size}"
        assert buffer.size                  == 0,       f"Buffer size expected to be 0 upon initialization, got {buffer.size}"
        assert buffer.is_ready_for_sampling == False,    "Buffer should not be ready for sampling upon initialization"
            
    def test_buffer_is_ready_for_sampling(self):
        """# Test is_ready_for_sampling Property of Experience Replay Buffer."""
        # Initialize buffer.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    4
                                            )
        
        # Verify not ready for sampling initially.
        assert buffer.is_ready_for_sampling     == False, "Buffer should not be ready for sampling initially"
        
        # Add transitions below batch size and verify not ready.
        for _ in range(3):
            buffer.push([0, 0], 0, 0.0, [0, 1], False)
            assert buffer.is_ready_for_sampling == False, "Buffer should not be ready for sampling when size is below batch size"
        
        # Add one more transition to reach batch size and verify ready.
        buffer.push([0, 0], 0, 0.0, [0, 1], False)
        assert buffer.is_ready_for_sampling     == True, "Buffer should be ready for sampling when size reaches batch size"
        
        # Add more transitions and verify remains ready.
        for _ in range(5):
            buffer.push([0, 0], 0, 0.0, [0, 1], False)
            assert buffer.is_ready_for_sampling == True, "Buffer should remain ready for sampling when size exceeds batch size"
            
    def test_buffer_max_capacity(self):
        """# Test Buffer Behavior at Maximum Capacity."""
        # Initialize buffer with small capacity.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      5,
                                                batch_size =    2
                                            )
        
        # Add transitions exceeding capacity.
        for i in range(10): buffer.push([i, i], i, float(i), [i + 1, i + 1], i % 2 == 0)
        
        # Verify size does not exceed capacity.
        assert buffer.size == buffer.capacity, f"Buffer size expected to be at capacity {buffer.capacity}, got {buffer.size}"
        
        # Sample batch and verify contents are from the most recent transitions.
        batch = buffer.sample()
        
        # Verify batch size.
        for transition in batch: assert transition.old_state[0] >= 5, "Sampled transitions should be from the most recent additions to the buffer"
            
    def test_buffer_sampling_custom_batch_size(self):
        """# Test Sampling with Custom Batch Size from Experience Replay Buffer."""
        # Initialize buffer and add transitions.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    4
                                            )
        
        # Push 10 transitions.
        for i in range(10): buffer.push([i, i], i, float(i), [i + 1, i + 1], i % 2 == 0)
        
        # Define custom batch size.
        custom_batch_size: int = 6
        
        # Sample batch with custom size.
        batch = buffer.sample(batch_size = custom_batch_size)
        
        # Verify batch size.
        assert len(batch) == custom_batch_size, f"Sampled batch size expected to be {custom_batch_size}, got {len(batch)}"
        
        # Verify batch contents.
        for transition in batch:
            assert isinstance(transition, tuple), "Each sampled item should be a Transition tuple"
            assert len(transition) == 5, "Each Transition tuple should have 5 components (old_state, action, reward, new_state, done)"
            
    def test_buffer_sampling_default_batch_size(self):
        """# Test Sampling with Default Batch Size from Experience Replay Buffer."""
        # Initialize buffer and add transitions.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    4
                                            )
        for i in range(10):
            buffer.push([i, i], i, float(i), [i + 1, i + 1], i % 2 == 0)
        
        # Sample batch without specifying size.
        batch = buffer.sample()
        
        # Verify batch size.
        assert len(batch) == buffer.batch_size, f"Sampled batch size expected to be {buffer.batch_size}, got {len(batch)}"
        
        # Verify batch contents.
        for transition in batch:
            assert isinstance(transition, tuple), "Each sampled item should be a Transition tuple"
            assert len(transition) == 5, "Each Transition tuple should have 5 components (old_state, action, reward, new_state, done)"
            
    def test_buffer_with_numpy_arrays(self):
        """# Test Experience Replay Buffer with Numpy Array States."""
        import numpy as np
        
        # Initialize buffer.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    4
                                            )
        
        # Add transitions with numpy array states.
        for i in range(10):
            old_state = np.array([i, i])
            action =    i
            reward =    float(i)
            new_state = np.array([i + 1, i + 1])
            done =      i % 2 == 0
            buffer.push(old_state, action, reward, new_state, done)
        
        # Sample batch.
        batch = buffer.sample()
        
        # Verify batch size.
        assert len(batch) == buffer.batch_size, f"Sampled batch size expected to be {buffer.batch_size}, got {len(batch)}"
        
        # Verify batch contents.
        for transition in batch:
            assert isinstance(transition, tuple), "Each sampled item should be a Transition tuple"
            assert len(transition) == 5, "Each Transition tuple should have 5 components (old_state, action, reward, new_state, done)"
            assert isinstance(transition[0], np.ndarray), "Old state should be a numpy array"
            assert isinstance(transition[3], np.ndarray), "New state should be a numpy array"
            
    def test_buffer_with_torch_tensors(self):
        """# Test Experience Replay Buffer with PyTorch Tensor States."""
        import torch
        
        # Initialize buffer.
        buffer: ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                capacity =      10,
                                                batch_size =    4
                                            )
        
        # Add transitions with torch tensor states.
        for i in range(10):
            old_state = torch.tensor([i, i])
            action =    i
            reward =    float(i)
            new_state = torch.tensor([i + 1, i + 1])
            done =      i % 2 == 0
            buffer.push(old_state, action, reward, new_state, done)
        
        # Sample batch.
        batch = buffer.sample()
        
        # Verify batch size.
        assert len(batch) == buffer.batch_size, f"Sampled batch size expected to be {buffer.batch_size}, got {len(batch)}"
        
        # Verify batch contents.
        for transition in batch:
            assert isinstance(transition, tuple), "Each sampled item should be a Transition tuple"
            assert len(transition) == 5, "Each Transition tuple should have 5 components (old_state, action, reward, new_state, done)"
            assert isinstance(transition[0], torch.Tensor), "Old state should be a torch tensor"
            assert isinstance(transition[3], torch.Tensor), "New state should be a torch tensor"