"""# lucidium.memory.replay.utilities.tests.sum_tree_test

Sum tree test suite.
"""

from pytest                                     import raises

from lucidium.memory.replay.utilities.sum_tree  import SumTree

# INITIALIZATION ===================================================================================

def test_sum_tree_initialization() -> None:
    """# Test Sum Tree Initialization."""
    # Initialize sum tree.
    tree:   SumTree =   SumTree(capacity = 4)
    
    # Validate properties.
    assert tree.total == 0.0,               \
        f"Sum tree total expected to be zero on initialization, got {tree.total}"
    assert tree.minimum == float("inf"),    \
        f"Sum tree minimum expected to be infinity on initialization, got {tree.minimum}"
        
def test_invalid_capacities() -> None:
    """# Test Invalid Tree Capacities."""
    # Ensure that capacities are required to be greater than zero.
    with raises(ValueError):    SumTree(capacity = 0)
    with raises(ValueError):    SumTree(capacity = -1)
    
# UPDATES ==========================================================================================

def test_update_single() -> None:
    """# Test Single Update."""
    # Initialize sum tree.
    tree:   SumTree =   SumTree(capacity = 4)
    
    # Make a single update.
    tree.update(index = 0, value = 5.0)
    
    # Validate properties.
    assert tree.total == 5.0,   f"Tree total expected to be 5.0, got {tree.total}"
    assert tree.minimum == 5.0, f"Tree minimum expected to be 5.0, got {tree.minimum}"
    
def  test_update_multiple() -> None:
    """# Test Multiple Updates."""
    # Initialize sum tree.
    tree:   SumTree =   SumTree(capacity = 4)
    
    # Make 4 updates.
    for i in range(4): tree.update(i, float(i + 1))
    
    # Validate properties.
    assert tree.total == 10.0,  f"Tree total expected to be 10.0, got {tree.total}"
    assert tree.minimum == 1.0, f"Tree minimum expected to be 1.0, got {tree.minimum}"
    
    
def test_overwrite() -> None:
    """# Test Overwriting a Node."""
    # Initialize sum tree.
    tree:   SumTree =   SumTree(capacity = 4)
    
    # Make initial update, then overwrite the node.
    tree.update(index = 0, value = 5.0)
    tree.update(index = 0, value = 10.0)
    
    # Validate properties.
    assert tree.total == 10.0,      f"Tree total expected to be 10.0, got {tree.total}"
    assert tree.minimum == 10.0,    f"Tree minimum expected to be 10.0, got {tree.minimum}"
    
# PREFIX SUM =======================================================================================

def test_find_prefix_sum() -> None:
    """# Test Finding a Prefix Sum."""
    # Initialize sum tree.
    tree:   SumTree =   SumTree(capacity = 4)
    
    # Make 4 updates.
    for i in range(4): tree.update(i, float(i + 1))
    
    # Validate finding various prefix sums.
    assert tree.find_prefix_sum_index(mass = 0.5) == 0,                     \
        f"Prefix sum = 0.5 expected at root node, but was found for node "  \
        f"{tree.find_prefix_sum_index(mass = 0.5)}"
    assert tree.find_prefix_sum_index(mass = 1.5) == 1,                     \
        f"Prefix sum = 0.5 expected at node 1, but was found for node "     \
        f"{tree.find_prefix_sum_index(mass = 1.5)}"
    assert tree.find_prefix_sum_index(mass = 4.0) == 2,                     \
        f"Prefix sum = 0.5 expected at node 2, but was found for node "     \
        f"{tree.find_prefix_sum_index(mass = 4.0)}"
    assert tree.find_prefix_sum_index(mass = 8.0) == 3,                     \
        f"Prefix sum = 0.5 expected at node 3, but was found for node "     \
        f"{tree.find_prefix_sum_index(mass = 8.0)}"