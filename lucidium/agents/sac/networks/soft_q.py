"""# lucidium.agents.sac.etworks.soft_q


"""

__all__ = ["SoftQNetwork"]

from typing                 import Callable

from torch                  import cat, Tensor
from torch.nn               import Linear, Module
from torch.nn.functional    import relu

class SoftQNetwork(Module):
    """# Soft Q-Network
    
    Soft Q-function Q_θ(s, a) used in SAC.

    This network estimates the expected *soft return* of taking action `a` in state `s` and then 
    following the current policy. Architecturally it's a standard MLP that maps the concatenated 
    (state, action) vector to a single scalar.

    ## Notes on shapes:
        * `state` is expected to be (B, state_dim)
        * `action` is expected to be (B, action_dim)
        * output is (B, 1)

    In SAC, you typically instantiate **two** independent copies (Q1 and Q2) with the same 
    architecture to implement *Clipped Double Q-learning*. This prevents overestimation bias by 
    using `min(Q1, Q2)` when forming targets.
    
    Adapted from: https://github.com/quantumiracle/Popular-RL-Algorithms/blob/master/sac.py
    """
    
    def __init__(self,
        state_dimension:    int,
        action_dimension:   int,
        hidden_dimension:   int =       256,
        activation:         Callable =  relu,
        initial_weight:     float =     3e-3
    ):
        """# Instantiate Soft Q-Network.

        ## Args:
            * state_dimension   (int):      Dimensionality of the (flattened) state vector.
            * action_dimension  (int):      Dimensionality of the (continuous) action vector.
            * hidden_dimension  (int):      Width of each hidden layer. Defaults to 256.
            * activation        (Callable): Activation functino to use in network. Defaults to relu.
            * initial_weight    (float):    Value used to initialize weights of output layer. 
                                            Defaults to 0.003.
        """
        # Initialize module.
        super(SoftQNetwork, self).__init__()

        # First linear layer takes concatenated [state, action] -> hidden_dim.
        self._linear_1_:    Linear =    Linear(in_features = state_dimension + action_dimension, out_features = hidden_dimension)

        # Second hidden layer keeps the same width -> hidden_dim.
        self._linear_2_:    Linear =    Linear(in_features = hidden_dimension,                   out_features = hidden_dimension)
        
        # Output head produces a single scalar Q-value per sample.
        self._linear_3_:    Linear =    Linear(in_features = hidden_dimension,                   out_features = 1)
        
        # Define activation function.
        self._activation_:  Callable =  activation
        
        # Initialize weights.
        self._linear_3_.weight.data.uniform_(-initial_weight, initial_weight)
        self._linear_3_.bias.data.uniform_(  -initial_weight, initial_weight)
        
        
    # METHODS ======================================================================================
    
    def disable_gradients(self) -> None:
        """# Disable Gradient Updates."""
        for parameter in self.parameters(): parameter.requires_grad_(False)
    
    def enable_gradients(self) -> None:
        """# Enable Gradient Updates."""
        for parameter in self.parameters(): parameter.requires_grad_(True)
    
    def forward(self,
        state:  Tensor,
        action: Tensor
    ) -> Tensor:
        """# Forward Pass through Network.

        ## Args:
            * state     (Tensor):   Batch of states.
            * action    (Tensor):   Batch of actions.

        ## Returns:
            * Tensor:   Predicated Q-values.

        ## Important:
            * The concatenation is along dim=1 (feature dimension), so state and action must share 
            the same batch size B.
            * No activation on the output; Q can be any real number.
        """
        return self._linear_3_(self._activation_(self._linear_2_(self._activation_(self._linear_1_(cat([state, action], 1))))))