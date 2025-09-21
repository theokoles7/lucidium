"""# lucidium.tabular.tests.q_table_test

Q-Table test suite.
"""

from typing                     import Any, Dict, List

from gymnasium.spaces           import Discrete
from numpy                      import all as np_all, array, ones, zeros
from numpy.testing              import assert_array_equal
from pytest                     import raises

from lucidium.tabular.q_table   import QTable

# INITIALIZATION ===================================================================================

def test_initialization():
    """Test Different Initialization Methods."""
    # Test with int action space.
    q_zeros:    QTable =    QTable(action_space = 3, initialization_method = "zeros")
    assert_array_equal(q_zeros[0], zeros(3)),                        \
        f"Q-Table initialization with zeros failed"
    
    # Test with Discrete action space.
    q_discrete: QTable =    QTable(action_space = Discrete(3), initialization_method = "zeros")
    assert_array_equal(q_discrete[0], zeros(3)),                     \
        f"Q-Table initialization with discrete action space failed"
    
    # Test optimistic initialization.
    q_opt:      QTable =    QTable(action_space = 3, initialization_method = "optimistic")
    assert_array_equal(q_opt[0], ones(3)),                           \
        f"Q-Table initialization with optimistic values failed"
    
    # Test random initialization bounds.
    q_random:   QTable =    QTable(action_space = 3, initialization_method = "random")
    assert np_all(q_random[0] >= -1.0) and np_all(q_random[0] <= 1.0),  \
        f"Q-Table initialization with random values failed."
    
    # Test small-random initialization bounds.
    q_small:    QTable =    QTable(action_space = 3, initialization_method = "small-random")
    assert np_all(q_small[0] >= -0.1) and np_all(q_small[0] <= 0.1),    \
        f"Q-Table initialization with small-random values failed"

def test_invalid_initialization():
    """Test Invalid Initialization."""
    # Test with invalid initialization method.
    with raises(AssertionError): QTable(action_space=2, initialization_method="invalid")
        
# STATE FORMATS ====================================================================================

def test_state_handling():
    """Test State Normalization and Access."""
    # Initialize q-table.
    q_table = QTable(action_space = 2)
    
    # Test different state formats
    state_formats:  Dict[str, Any] =    {
                                            "int":      1,
                                            "list":     [1.0, 2.0],
                                            "tuple":    (1.0, 2.0),
                                            "ndarray":  array([1.0, 2.0])
                                        }
    
    # For each state data type...
    for state_type, state in state_formats.items():
        
        # Assign value to state.
        q_table[state, 0] = 1.0
        
        # Verify that state was assigned correctly.
        assert q_table[state][0] == 1.0,    \
            f"Value assignment failed for {state_type} state"
            
# CONTAINS =========================================================================================

def test_value_operations():
    """Test Setting and Getting Values."""
    # Initialize q-table.
    q_table:    QTable =    QTable(action_space = 3)
    
    # Set value..
    q_table[0, 1] =         0.5
    
    # Ensure that value was properly assigned.
    assert q_table[0][1] == 0.5,    \
        f"Assigned value expected to be 0.5, got {q_table[0][1]}"
    
    # Ensure that __contains__ is operational.
    assert 0 in q_table,        \
        f"Value 0 expected to be in Q-Table"
    assert 999 not in q_table,  \
        f"Value 999 expected to not be in Q-Table"
        
# VALUE RETRIEVAL ==================================================================================

def test_best_actions():
    """Test Best Action/Value Selection."""
    # Initialize q-table.
    q_table:    QTable =    QTable(action_space = 3)
    
    # Set up known values.
    q_table[0, 0] =         0.1
    q_table[0, 1] =         0.5
    q_table[0, 2] =         0.3
    
    # Validate best action and value.
    assert q_table.get_best_action(0) == 1,     \
        f"Best action expected to be 1, got {q_table.get_best_action(0)}"
    assert q_table.get_best_value(0)  == 0.5,   \
        f"Best value expected to be 0.5, got {q_table.get_best_value(0)}"
        
# SERIALIZATION ====================================================================================

def test_serialization(tmp_path):
    """Test Serialization and File Operations."""
    # Initialize Q-Table.
    q_table:    QTable =                    QTable(action_space = 2)
    
    # Assign values.
    q_table[0, 0] =                         0.5
    q_table[0, 1] =                         0.7
    
    # Serialize Q-Table.
    serialized: Dict[Any, List[float]] =    q_table.serialize()
    
    # Ensure that a dictionary was provided.
    assert isinstance(serialized, dict),    \
        f"Expected serialization to provide dictionary, got {type(serialized)}"
    
    # Define a temporary path to save table.
    save_path:  str =                       tmp_path / "q_table.json"
    
    # Save table to file.
    q_table.save(save_path)
    
    # Initialize a new Q-Table for comparison.
    new_table:  QTable =                    QTable(action_space = 2)
    
    # Load table from file.
    new_table.load(save_path)
    
    # Ensure that table state was preserved.
    assert_array_equal(q_table[0], new_table[0]),   \
        f"Table loaded from file does not match original state"

