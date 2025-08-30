"""# lucidium.memory.tests.test_transition

Test suite for lucidium.memory.transition.
"""

from lucidium.memory.transition import Transition

class TestTransition():
    """Transition Test Suite."""
    # Define first set of transition components.
    old_state = [1, 2]
    action =    0
    reward =    1.0
    new_state = [3, 4]
    done =      False
    
    # Define second set of transition components.
    alt_old_state = [5, 6]
    alt_action =    1
    alt_reward =    0.5
    alt_new_state = [7, 8]
    alt_done =      True

    def test_transistion_equality(self):
        """# Test Equality of Transitions."""
        # Initialize two identical transitions.
        transition1:    Transition =    Transition(self.old_state, self.action, self.reward, self.new_state, self.done)
        transition2:    Transition =    Transition(self.old_state, self.action, self.reward, self.new_state, self.done)
        transition3:    Transition =    Transition(self.alt_old_state, self.alt_action, self.alt_reward, self.alt_new_state, self.alt_done)
        
        # Verify equality.
        assert transition1  ==  transition2, "Transitions with identical components should be equal"
        assert transition1  !=  transition3, "Transitions with different components should not be equal"
        
    def test_transition_indexing(self):
        """# Test Indexing of Transition."""
        # Initialize transition.
        transition: Transition =    Transition(self.old_state, self.action, self.reward, self.new_state, self.done)
        
        # Verify indexing.
        assert self.old_state   == transition[0],   f"Old state expected to be {self.old_state}, got {transition[0]}"
        assert self.action      == transition[1],   f"Action expected to be {self.action}, got {transition[1]}"
        assert self.reward      == transition[2],   f"Reward expected to be {self.reward}, got {transition[2]}"
        assert self.new_state   == transition[3],   f"New state expected to be {self.new_state}, got {transition[3]}"
        assert self.done        == transition[4],   f"Done expected to be {self.done}, got {transition[4]}"

    def test_transition_initialization(self):
        """# Test Default Initialization of Transition."""
        # Initialize transition.
        transition: Transition = Transition(self.old_state, self.action, self.reward, self.new_state, self.done)
        
        # Verify initialization.
        assert self.old_state   == transition.old_state,    f"Old state expected to be {self.old_state}, got {transition.old_state}"
        assert self.action      == transition.action,       f"Action expected to be {self.action}, got {transition.action}"
        assert self.reward      == transition.reward,       f"Reward expected to be {self.reward}, got {transition.reward}"
        assert self.new_state   == transition.new_state,    f"New state expected to be {self.new_state}, got {transition.new_state}"
        assert self.done        == transition.done,         f"Done expected to be {self.done}, got {transition.done}"
        
    def test_transition_unpacking(self):
        """# Test Unpacking of Transition."""
        # Initialize transition.
        transition: Transition =    Transition(self.old_state, self.action, self.reward, self.new_state, self.done)
        
        # Unpack transition.
        unpacked_old_state, unpacked_action, unpacked_reward, unpacked_new_state, unpacked_done =   transition
        
        # Verify unpacking.
        assert self.old_state   == unpacked_old_state,  f"Old state expected to be {self.old_state}, got {unpacked_old_state}"
        assert self.action      == unpacked_action,     f"Action expected to be {self.action}, got {unpacked_action}"
        assert self.reward      == unpacked_reward,     f"Reward expected to be {self.reward}, got {unpacked_reward}"
        assert self.new_state   == unpacked_new_state,  f"New state expected to be {self.new_state}, got {unpacked_new_state}"
        assert self.done        == unpacked_done,       f"Done expected to be {self.done}, got {unpacked_done}"
        
    def test_transition_with_torch_tensors(self):
        """# Test Transition with PyTorch Tensors."""
        import torch
        
        # Define transition components as tensors.
        old_state = torch.tensor(self.old_state)
        action =    torch.tensor(self.action)
        reward =    torch.tensor(self.reward)
        new_state = torch.tensor(self.new_state)
        done =      torch.tensor(self.done)
        
        # Initialize transition.
        transition: Transition =    Transition(old_state, action, reward, new_state, done)
        
        # Verify initialization.
        assert torch.equal(old_state, transition.old_state),    f"Old state expected to be {old_state}, got {transition.old_state}"
        assert torch.equal(action, transition.action),          f"Action expected to be {action}, got {transition.action}"
        assert torch.equal(reward, transition.reward),          f"Reward expected to be {reward}, got {transition.reward}"
        assert torch.equal(new_state, transition.new_state),    f"New state expected to be {new_state}, got {transition.new_state}"
        assert torch.equal(done, transition.done),              f"Done expected to be {done}, got {transition.done}"
        
    def test_transition_with_numpy_arrays(self):
        """# Test Transition with NumPy Arrays."""
        import numpy as np
        
        # Define transition components as numpy arrays.
        old_state = np.array(self.old_state)
        action =    np.array(self.action)
        reward =    np.array(self.reward)
        new_state = np.array(self.new_state)
        done =      np.array(self.done)
        
        # Initialize transition.
        transition: Transition =    Transition(old_state, action, reward, new_state, done)
        
        # Verify initialization.
        assert np.array_equal(old_state, transition.old_state), f"Old state expected to be {old_state}, got {transition.old_state}"
        assert np.array_equal(action, transition.action),       f"Action expected to be {action}, got {transition.action}"
        assert np.array_equal(reward, transition.reward),       f"Reward expected to be {reward}, got {transition.reward}"
        assert np.array_equal(new_state, transition.new_state), f"New state expected to be {new_state}, got {transition.new_state}"
        assert np.array_equal(done, transition.done),           f"Done expected to be {done}, got {transition.done}"
