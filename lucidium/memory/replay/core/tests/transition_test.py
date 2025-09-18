"""# lucidium.memory.replay.core.tests.transition_test

Transition test suite.
"""

from numpy                                  import array, array_equal
from numpy.typing                           import NDArray
from pytest                                 import raises

from lucidium.memory.replay.core.transition import Transition

# INITIALIZATION ===================================================================================

def test_transition_initialization() -> None:
    """# Test Transition Initialization."""
    # Define parameters.
    state:      NDArray =       array([1, 2, 3])
    action:     int =           0
    reward:     float =         1.0
    next_state: NDArray =       array([2, 3, 4])
    done:       bool =          False
    
    # Initialize transition.
    transition: Transition =    Transition(
                                    state =         state,
                                    action =        action,
                                    reward =        reward,
                                    next_state =    next_state,
                                    done =          done
                                )
    
    # Validate parameters.
    assert array_equal(transition.state, state),            \
        f"Transition state expected to be {state}, got {transition.state}"
    assert transition.action == action,                     \
        f"Transition action expected to be {action}, got {transition.action}"
    assert transition.reward == reward,                     \
        f"Transition reward expected to be {reward}, got {transition.reward}"
    assert array_equal(transition.next_state, next_state),  \
        f"Transistion next state expected to be {next_state}, got {transition.next_state}"
    assert transition.done == done,                         \
        f"Transition done expected to be {done}, got {transition.done}"
        
def test_transition_initialization_with_array_action() -> None:
    """# Test Transition Initization with Array Action."""
    # Initialize array action.
    action: NDArray =   array([0.5, -0.3])
    
    # Initialize transition.
    transition: Transition =    Transition(
                                    state =         array([1, 2]),
                                    action =        action,
                                    reward =        1.0,
                                    next_state =    array([2, 3]),
                                    done =          False
                                )
    
    # Ensure that action was defined properly.
    assert array_equal(action, transition.action), \
        f"Transition action expected to be {action}, got {transition.action}"
        
# IMMUTABILITY =====================================================================================

def test_transition_immutability() -> None:
    """# Test Transition Immutability."""
    # Initialize transition.
    transition: Transition =    Transition(
                                    state =         array([1, 2]),
                                    action =        0,
                                    reward =        1.0,
                                    next_state =    array([2, 3]),
                                    done =          False
                                )
    
    # Ensure that modifying properties raises errors.
    with raises(AttributeError): transition.state =         array([1, 2, 3])
    with raises(AttributeError): transition.action =        1
    with raises(AttributeError): transition.reward =        2.0
    with raises(AttributeError): transition.next_state =    array([2, 3, 4])
    with raises(AttributeError): transition.done =          True