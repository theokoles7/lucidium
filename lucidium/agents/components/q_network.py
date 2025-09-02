"""# lucidium.agents.components.q_network

Defines the structure and utility of the Q-Network.
"""

__all__ = ["QNetwork"]

from logging                import Logger

from torch                  import manual_seed, Tensor
from torch.nn               import Linear, Module
from torch.nn.functional    import relu

from lucidium.utilities     import get_child

class QNetwork(Module):
    """# Q-Network

    Network used to model the relationship between observations/states and the "quality" of actions 
    that could be taken in those states.
    """
    
    def __init__(self,
        observation_size:       int,
        action_size:            int,
        layer_1_output_size:    int =   128,
        layer_2_output_size:    int =   128,
        random_seed:            int =   42
    ):
        """# Instantiate Q-Network.

        ## Args:
            * observation_size      (int):  Size of observation tensors.
            * action_size           (int):  Number of actions accounted for in output.
            * layer_1_output_size   (int):  Size of first layer's output. Defaults to 128.
            * layer_2_output_size   (int):  Size of second layer's output. Defaults to 128.
        """
        # Initialize module.
        super(QNetwork, self).__init__()
        
        # Initialize logger.
        self.__logger__:    Logger =    get_child("q-network")
        
        # Define layers.
        self._fc_1_:        Linear =    Linear(in_features = observation_size,    out_features = layer_1_output_size)
        self._fc_2_:        Linear =    Linear(in_features = layer_1_output_size, out_features = layer_2_output_size)
        self._fc_3_:        Linear =    Linear(in_features = layer_2_output_size, out_features = action_size)
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized Q-Network ({locals()})")
        
    # METHODS ======================================================================================
    
    def forward(self,
        observation:    Tensor
    ) -> Tensor:
        """# Forward Pass through Q-Network.

        ## Args:
            * observation   (Tensor):   Observation (input) tensor.

        ## Returns:
            * Tensor:   Action (output) tensor.
        """
        # Debug observation shape.
        self.__logger__.debug(f"Observation (input) shape: {observation.shape}")
        
        # Pass through layer 1.
        X:          Tensor =    relu(self._fc_1_(observation))
        
        # Debug layer 1 output shape.
        self.__logger__.debug(f"Layer 1 output shape: {X.shape}")
        
        # Pass through layer 2.
        X:          Tensor =    relu(self._fc_2_(X))
        
        # Debug layer 2 output shape.
        self.__logger__.debug(f"Layer 2 output shape: {X.shape}")
        
        # Pass through layer 3.
        actions:    Tensor =    self._fc_3_(X)
        
        # Debug actions shape.
        self.__logger__.debug(f"Layer 3 (actions output) shape: {actions.shape}")
        
        # Provide actions.
        return actions
    
    # HELPERS ======================================================================================
    
    def _seed_(self,
        random_seed:    int
    ) -> None:
        """# Seed Q-Network.
        
        Set the random seed so that initialization and stochastic operations are reproducible.

        ## Args:
            * random_seed   (int):  Random seed.
        """
        # Set the seed for generating random numbers on all devices.
        manual_seed(seed = random_seed)
        
        # Debug seed.
        self.__logger__.debug(f"Seeded Q-Network with seed = {random_seed}")