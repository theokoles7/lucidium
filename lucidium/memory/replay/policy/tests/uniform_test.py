"""# lucidium.memory.replay.policy.tests.uniform_test

Uniform sampling policy test suite.
"""

from pytest                                 import raises

from lucidium.memory.replay.policy.uniform  import UniformSampling

# INITIALIZATION ===================================================================================

def test_uniform_sampling_init() -> None:
    """# Test Initialization of Uniform Sampling Policy."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Validate properties.
    assert policy.capacity == 100, f"Policy capacity expected to be 100, got {policy.capacity}"
    
# TRANSITION PUSH CALLBACK =========================================================================

def test_on_add() -> None:
    """# Test On-Add Callback (No-op)"""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Call on add, which should raise no exceptions.
    policy.on_add(index = 0, priority = 1.0)
    policy.on_add(index = 1)
    
# RESET ============================================================================================

def test_policy_reset() -> None:
    """# Test Reseting the Policy."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Reset policy with new capacity.
    policy.reset(capacity = 200)
    
    # Ensure new capacity registered.
    assert policy.capacity == 200, f"New policy capacity expected to be 200, got {policy.capacity}"
    
# SAMPLING =========================================================================================

def test_uniform_sampling() -> None:
    """# Test Unifrom Sampling."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Sample from policy.
    indices, weights =          policy.sample(sample_range = 50, batch_size = 10)
    
    # Validate results.
    assert len(indices) == 10,                      \
        f"Length of sampled indices expected to be 10, got {len(indices)}"
    assert weights is None,                         \
        f"Sample weights expected to be None (no weights used in uniform policy), got {weights}"
    assert all(0 <= idx < 50 for idx in indices),   \
        f"Sampled indices found to be outside of intended range"

def test_sampling_empty_buffer() -> None:
    """# Test Uniform Sampling on Empty Buffer."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Ensure early sampling raises error.
    with raises(RuntimeError): policy.sample(sample_range = 0, batch_size = 10)
    
# NO-OPS ===========================================================================================

def test_policy_step() -> None:
    """# Test Uniform Policy Step (No-op)."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Simply ensure that no exception is raised for no-op.
    policy.step()
    
def test_priority_update() -> None:
    """# Test Updating Priorities (No-op)."""
    # Initialize policy.
    policy: UniformSampling =   UniformSampling(capacity = 100)
    
    # Simply ensure that no exception is raised for no-op.
    policy.update_priorities(indices = [0, 1], td_errors = [1.0, 2.0])