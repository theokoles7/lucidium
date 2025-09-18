"""# lucidium.memory.replay.policy.tests.prioritized_test

Prioritized sampling policy test suite.
"""

from pytest                                     import raises, warns

from lucidium.memory.replay.policy.prioritized  import PrioritizedSampling

# INITIALIZATION ===================================================================================

def test_init_default() -> None:
    """# Test Default Initialization."""
    # Initialize policy with no arguments.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100)
    
    # Validate default properties.
    assert policy.capacity == 100,              \
        f"Policy capacity expected to be 100, got {policy.capacity}"
    assert policy.alpha == 0.6,                 \
        f"Default policy alpha expected to be 0.6, got {policy.alpha}"
    assert policy.beta  == 0.4,                 \
        f"Default policy beta expected to be 0.4, got {policy.beta}"
    assert policy.beta_start == 0.4,            \
        f"Default policy beta expected to be 0.4, got {policy.beta_start}"
    assert policy.beta_end == 1.0,              \
        f"Default policy beta end expected to be 1.0, got {policy.beta_end}"
    assert policy.beta_anneal_steps == 200000,  \
        f"Default policy beta anneal steps expected to be 200,000, got {policy.beta_anneal_steps}"
    assert policy.epsilon == 1e-6,              \
        f"Default policy epsilon expected to be 0.000001, got {policy.epsilon}"
    assert policy.default_priority == 1.0,      \
        f"Default policy priority expected to be 1.0, got {policy.default_priority}"
        
def test_init_custom() -> None:
    """# Test Custom Initialization."""
    # Initialize policy with arguments.
    policy: PrioritizedSampling =   PrioritizedSampling(
                                        capacity =          50,
                                        alpha =             0.8,
                                        beta_start =        0.2,
                                        beta_end =          0.9,
                                        beta_anneal_steps = 1000,
                                        epsilon =           1e-5,
                                        default_priority =  2.0
                                    )
    
    # Validate custom properties.
    assert policy.capacity == 50,               \
        f"Policy capacity expected to be 50, got {policy.capacity}"
    assert policy.alpha == 0.8,                 \
        f"Default policy alpha expected to be 0.8, got {policy.alpha}"
    assert policy.beta  == 0.2,                 \
        f"Default policy beta expected to be 0.2, got {policy.beta}"
    assert policy.beta_start == 0.2,            \
        f"Default policy beta expected to be 0.2, got {policy.beta_start}"
    assert policy.beta_end == 0.9,              \
        f"Default policy beta end expected to be 0.9, got {policy.beta_end}"
    assert policy.beta_anneal_steps == 1000,    \
        f"Default policy beta anneal steps expected to be 1,000, got {policy.beta_anneal_steps}"
    assert policy.epsilon == 1e-5,              \
        f"Default policy epsilon expected to be 0.00001, got {policy.epsilon}"
    assert policy.default_priority == 2.0,      \
        f"Default policy priority expected to be 2.0, got {policy.default_priority}"
        
def test_init_invalid() -> None:
    """# Test Invalid Initialization."""
    # Ensure that invalid parameters cause errors.
    with raises(AssertionError): PrioritizedSampling(capacity = 0)
    with raises(AssertionError): PrioritizedSampling(capacity = 1, alpha = -1.0)
    with raises(AssertionError): PrioritizedSampling(capacity = 1, beta_start = -1.5)
    with raises(AssertionError): PrioritizedSampling(capacity = 1, beta_start = 1.5)
    with raises(AssertionError): PrioritizedSampling(capacity = 1, beta_end = 1.5)
    with raises(AssertionError): PrioritizedSampling(capacity = 1, beta_end = -1.5)
    
# CALLBACKS ========================================================================================

def test_on_add() -> None:
    """# Test On-Add Callback."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100)
    
    # Call twice, once with no priority measure.
    policy.on_add(index = 0, priority = 2.0)
    policy.on_add(index = 1)
    
    # Ensure priorities are initialized properly.
    assert policy.get_priority(0) > 0,  f"Priority was not set"
    assert policy.get_priority(1) > 0,  f"Priority was not set"
    
# LIFE CYCLE =======================================================================================

def test_reset() -> None:
    """# Test Policy Reset."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100, alpha = 0.8)
    
    # Add priorities.
    for i in range(3): policy.on_add(index = i, priority = float(i + 1))
    
    # Validate pre-condition.
    assert policy.tree.total > 0,   \
        f"Policy sum tree total expected to be greater than zero, got {policy.tree.total}"
        
    # Reset policy with new capacity.
    policy.reset(capacity = 200)
    
    # Validate post-condition.
    assert policy.capacity == 200,  \
        f"New policy capacity expected to be 200, got {policy.capacity}"
    assert policy.alpha == 0.8,     \
        f"Policy alpha expected to be preserved at 0.8, got {policy.alpha} after reset"
    assert policy.tree.total == 0,  \
        f"Policy sum tree total expected to be zero after reset, got {policy.tree.total}"
        
# SAMPLING =========================================================================================

def test_sampling() -> None:
    """# Test Prioritized Sampling."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100)
    
    # Add priorities.
    for i in range(3): policy.on_add(index = i, priority = float(i + 1))
    
    # Sample from policy.
    indices, weights =              policy.sample(sample_range = 3, batch_size = 5)
    
    # Ensure that 5 samples were provided.
    assert len(indices) == 5,                           \
        f"Expected 5 index samples, got {len(indices)}"
    assert len(weights) == 5,                           \
        f"Expected 5 weight samples, got {len(weights)}"
    
    # Ensure proper range of samples.
    assert all(0 <= index <= 3 for index in indices),   \
        f"Inidices found to be outside of expected range [0, 3]"
    assert all(0 <= weight <= 1 for weight in weights), \
        f"Weights found to be outside of expected range [0, 1]"
        
def test_sampling_empty_buffer() -> None:
    """# Test Prioritized Sampling from an Empty Buffer."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100)
    
    # Ensure sampling from empty buffer raises an error.
    with raises(RuntimeError): policy.sample(sample_range = 0, batch_size = 10)

def test_sampling_zero_priorities() -> None:
    """# Test Sampling When all Priorities are Zero."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100, epsilon = 0.0)
    
    # Sample from policy, ignoring warning of zero sum.
    with warns(UserWarning, match="Priority sum is no longer positive*"):
        indices, weights =              policy.sample(sample_range = 3, batch_size = 5)
    
    # Validate sampling results.
    assert len(indices) == 5,                           \
        f"Expected 5 index samples, got {len(indices)}"
    assert len(weights) == 5,                           \
        f"Expected 5 weight samples, got {len(weights)}"
    
    # Ensure proper range of samples.
    assert all(weight == 1.0 for weight in weights),    \
        f"All weights expected to be default of 1.0, got {weights}"
        
# ANNEALING BETA ===================================================================================

def test_beta_annealing() -> None:
    """# Test Beta Annealing."""
    # Initialize policy.
    policy:     PrioritizedSampling =   PrioritizedSampling(
                                            capacity =          100,
                                            beta_start =        0.4,
                                            beta_end =          1.0,
                                            beta_anneal_steps = 100
                                        )
    
    # Record initial beta value.
    init_beta:  float =                 policy.beta
    
    # Simulate 50 steps.
    for _ in range(50): policy.step()
    
    # Record resulting beta value.
    mid_beta:   float =                 policy.beta
    
    # Simulate 50 steps.
    for _ in range(50): policy.step()
    
    # Record resulting beta value.
    final_beta: float =                 policy.beta
    
    # Validate range.
    assert init_beta < mid_beta < final_beta,   \
        f"Beta ranges incorrect: beta_t_0 = {init_beta}, beta_t_50 = {mid_beta}, beta_t_100 = {final_beta}"
    assert final_beta == 1.0,                   \
        f"Final beta value expected to be 1.0, got {final_beta}"
        
# PRIORITIES =======================================================================================

def test_priority_update() -> None:
    """# Test Updating Priorities."""
    # Initialize policy.
    policy: PrioritizedSampling =   PrioritizedSampling(capacity = 100)
    
    # Add priorities.
    for i in range(3): policy.on_add(index = i, priority = float(i + 1))
    
    # Record initial sum tree total.
    initial_total:  float = policy.tree.total
    
    # Update priorities.
    policy.update_priorities(indices = [0, 1], td_errors = [5.0, 10.0])
    
    # Record new total.
    new_total:      float = policy.tree.total
    
    # Ensure that priorities were updated.
    assert new_total > initial_total,   \
        f"New total {new_total} expected to be greater than initial total {initial_total}"