"""# lucidium.memory.replay.core.tests.batch_test

Transition batch test suite.
"""

from typing                                 import List

from numpy                                  import array, array_equal
from numpy.typing                           import NDArray
from pytest                                 import raises

from lucidium.memory.replay.core.batch      import Batch
from lucidium.memory.replay.core.transition import Transition

# INITIALIZATION ===================================================================================

def test_batch_initialization() -> None:
    """# Test Batch Initialization."""
    # Initialize a couple of dummy transitions.
    transitions:    List[Transition] =  [
                                            Transition(
                                                state =         array([1]),
                                                action =        0,
                                                reward =        1.0,
                                                next_state =    array([2]),
                                                done =          False
                                            ),
                                            Transition(
                                                state =         array([3]),
                                                action =        1,
                                                reward =        2.0,
                                                next_state =    array([4]),
                                                done =          True
                                            )
                                        ]
    
    # Define dummy indices.
    indices:        NDArray =           array([0, 1])
    
    # Define dummy importance.
    importance:     NDArray =           array([0.5, 1.0])
    
    # Instantiate batch.
    batch:          Batch =             Batch(
                                            transitions =   transitions,
                                            indices =       indices,
                                            importance =    importance
                                        )
    
    # Validate properties.
    assert len(batch) == 2,                             \
        f"Batch length expected to be 2, got {len(batch)}"
    assert array_equal(indices,    batch.indices),      \
        f"Batch indices expected to be {indices}, got {batch.indices}"
    assert array_equal(importance, batch.importance),   \
        f"Batch importance expected to be {importance}, got {batch.importance}"
        
def test_batch_optional_fields() -> None:
    """# Test Optional Fields of Batch Initialization."""
    # Initialize a couple of dummy transitions.
    transitions:    List[Transition] =  [
                                            Transition(
                                                state =         array([1]),
                                                action =        0,
                                                reward =        1.0,
                                                next_state =    array([2]),
                                                done =          False
                                            )
                                        ]
    
    # Instantiate batch without indices or importance.
    batch:          Batch =             Batch(transitions = transitions)
    
    # Validate properties.
    assert len(batch) == 1,             \
        f"Batch length expected to be 2, got {len(batch)}"
    assert batch.indices    is None,    \
        f"Batch indices expected to be None, got {batch.indices}"
    assert batch.importance is None,    \
        f"Batch importance expected to be None, got {batch.importance}"
        
# IMMUTABILITY =====================================================================================

def test_batch_immutability() -> None:
    """# Test Batch Immutability."""
    # Initialize a couple of dummy transitions.
    transitions:    List[Transition] =  [
                                            Transition(
                                                state =         array([1]),
                                                action =        0,
                                                reward =        1.0,
                                                next_state =    array([2]),
                                                done =          False
                                            ),
                                            Transition(
                                                state =         array([3]),
                                                action =        1,
                                                reward =        2.0,
                                                next_state =    array([4]),
                                                done =          True
                                            )
                                        ]
    
    # Define dummy indices.
    indices:        NDArray =           array([0, 1])
    
    # Define dummy importance.
    importance:     NDArray =           array([0.5, 1.0])
    
    # Instantiate batch.
    batch:          Batch =             Batch(
                                            transitions =   transitions,
                                            indices =       indices,
                                            importance =    importance
                                        )
    
    # Ensure that modifying properties raises errors.
    with raises(AttributeError): batch.transitions =    transitions
    with raises(AttributeError): batch.indices =        indices
    with raises(AttributeError): batch.importance =     importance