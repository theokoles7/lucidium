"""# lucidium.optimization.reinforce.tests.reinforce_test

Tests for the Reinforce loss function.
"""

from torch                              import float32, int64, isfinite, tensor, Tensor

from lucidium.optimization.reinforce    import ReinforceLoss

class TestReinforceLoss():
    """# Reinforce Loss Test Suite."""
    
    def test_reinforce_loss_initialization(self):
        """# Test Initialization of Reinforce Loss."""
        # Initialize Reinforce loss without entropy regularization.
        assert ReinforceLoss()._entropy_beta_ is None, "Entropy beta should be None when not provided"
        
        # Define an arbitrary entropy beta value.
        entropy_beta_value:             float =         0.01
        
        # Instantiate Reinforce loss with entropy regularization.
        reinforce_loss_with_entropy:    ReinforceLoss = ReinforceLoss(entropy_beta=entropy_beta_value)
        
        # Verify entropy beta is set correctly.
        assert reinforce_loss_with_entropy._entropy_beta_ == entropy_beta_value, \
            f"Entropy beta should be {entropy_beta_value} when provided"
        
    def test_reinforce_loss_forward(self):
        """# Test Forward Pass of Reinforce Loss."""
        # Create dummy inputs.
        batch_size:         int =           4
        num_actions:        int =           3
        
        # Define a batch of policy distributions (probabilities for each action).
        policy:             Tensor =        tensor(
                                                [
                                                    [0.7, 0.2, 0.1],
                                                    [0.1, 0.8, 0.1],
                                                    [0.3, 0.4, 0.3],
                                                    [0.25, 0.25, 0.5]
                                                ],
                                                dtype = float32
                                            )
        
        # Define an actino to take.
        action:             Tensor =        tensor([0, 1, 2, 2], dtype = int64)
        
        # Define discounted rewards.
        discount_reward:    Tensor =        tensor([1.0, 0.5, 1.5, 2.0], dtype = float32)
        
        # Initialize Reinforce loss with entropy regularization.
        entropy_beta_value: float =         0.01
        
        # Instantiate Reinforce loss.
        reinforce_loss:     ReinforceLoss = ReinforceLoss(entropy_beta = entropy_beta_value)
        
        # Compute loss and monitors.
        loss, monitors =                    reinforce_loss.forward(
                                                policy =            policy,
                                                action =            action,
                                                discount_reward =   discount_reward,
                                                entropy_beta =      None
                                            )
        
        # Verify outputs.
        assert isinstance(loss, Tensor),                    "Loss should be a Tensor"
        assert loss.dim() == 0,                             "Loss should be a scalar tensor"
        assert isinstance(monitors, dict),                  "Monitors should be a dictionary"
        assert "reinforce_loss" in monitors,                "Monitors should contain 'reinforce_loss'"
        assert "entropy_loss" in monitors,                  "Monitors should contain 'entropy_loss'"
        
        # Check that the losses are finite numbers.
        assert isfinite(loss).item(),                       "Loss should be a finite number"
        assert isfinite(monitors["reinforce_loss"]).item(), "'reinforce_loss' should be a finite number"
        assert isfinite(monitors["entropy_loss"]).item(),   "'entropy_loss' should be a finite number"