"""# lucidium.agents.sac.networks.value

Soft state value function for Soft Actor-Critic.
"""

__all__ = ["ValueNetwork"]

from logging                import Logger
from typing                 import Callable

from torch                  import Tensor
from torch.nn               import Linear, Module
from torch.nn.functional    import relu

from lucidium.utilities     import get_child

class ValueNetwork(Module):
    """# Value Network

    Soft state value function for Soft Actor-Critic.
    
    Adapted from: https://github.com/quantumiracle/Popular-RL-Algorithms/blob/master/sac.py
    """
    
    def __init__(self,
        state_dimension:    int,
        hidden_dimension:   int =       256,
        activation:         Callable =  relu,
        initial_weight:     float =     3e-3
    ):
        """# Instantiate Value Network.

        ## Args:
            * state_dimension   (int):      Size of state dimension.
            * hidden_dimension  (int):  S   ize of hidden dimension. Defaults to 256.
            * activation        (Callable): Activation functino to use in network. Defaults to relu.
            * initial_weight    (float):    Value used to initialize weights of output layer. 
                                            Defaults to 0.003.
        """
        # Initialize module.
        super(ValueNetwork, self).__init__()
        
        # Initialize logger.
        self.__logger__:    Logger =    get_child("value")
        
        # Define layers.
        self._linear_1_:    Linear =    Linear(in_features = state_dimension,   out_features = hidden_dimension)
        self._linear_2_:    Linear =    Linear(in_features = hidden_dimension,  out_features = hidden_dimension)
        self._linear_3_:    Linear =    Linear(in_features = hidden_dimension,  out_features = 1)
        
        # Define activation function.
        self._activation_:  Callable =  activation
        
        # Initialize weights.
        self._linear_3_.weight.data.uniform_(-initial_weight, initial_weight)
        self._linear_3_.bias.data.uniform_(  -initial_weight, initial_weight)
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized Value network ({locals()})")
        
    # METHODS ======================================================================================
    
    def disable_gradients(self) -> None:
        """# Disable Gradient Updates."""
        for parameter in self.parameters(): parameter.requires_grad_(False)
    
    def enable_gradients(self) -> None:
        """# Enable Gradient Updates."""
        for parameter in self.parameters(): parameter.requires_grad_(True)
    
    def forward(self,
        state:  Tensor
    ) -> Tensor:
        """# Forward Pass through Network.

        ## Args:
            * state (Tensor):   State tensor.

        ## Returns:
            * Tensor:   Value of possible actions at this state.
        """
        # Debug state shape.
        self.__logger__.debug(f"State input shape: {state.shape}")
        
        # Pass through first layer.
        X:  Tensor =    self._activation_(self._linear_1_(state))
        
        # Debug layer 1 output shape.
        self.__logger__.debug(f"Layer 1 output shape: {X.shape}")
        
        # Pass through second layer.
        X:  Tensor =    self._activation_(self._linear_2_(X))
        
        # Debug layer 2 output shape.
        self.__logger__.debug(f"Layer 2 output shape: {X.shape}")
        
        # Pass through third/output layer.
        X:  Tensor =    self._linear_3_(X)
        
        # Debug final output shape.
        self.__logger__.debug(f"Final output shape: {X.shape}")
        
        # Provide output.
        return X