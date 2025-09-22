"""# lucidium.neural.q_network

Q-network implementation.
"""

__all__ = ["QNetwork"]

from logging                    import Logger
from typing                     import Tuple, Union

from gymnasium.spaces           import Discrete, Space
from numpy.typing               import NDArray
from torch                      import dtype, float32, Tensor
from torch.nn                   import Module, ReLU, Sequential

from lucidium.neural.utilities  import create_mlp, extract_space_size
from lucidium.utilities         import get_child

class QNetwork(Module):
    """# Q-Network.

    Network used to model the relationship between observations/states and the "quality" of actions 
    that could be taken in those states.
    """
    
    def __init__(self,
        observation_space:      Space,
        action_space:           Discrete,
        hidden_size:            Union[int, Tuple[int, ...]] =   (64, 64),
        activation:             type[Module] =                  ReLU,
        squash_output:          bool =                          False,
        bias:                   bool =                          True,
        device:                 str =                           "cpu",
        data_type:              dtype =                         float32
    ):
        """# Instantiate Multi-Layer Perceptron.

        ## Args:
            * observation_space (Space):            Environment observation space.
            * action_space      (Discrete):         Environment action space.
            * hidden_size       (int | Tuple[int]): Size(s) of hidden connections. Defaults to (64, 
                                                    64).
            * activation        (Module):           Activation function to use between layers. 
                                                    Defaults to ReLU.
            * squash_output     (bool):             If true, output will be squashed using 
                                                    hyberbolic tangent. Defaults to False.
            * bias              (bool):             If true, layers will learn additive bias. 
                                                    Defaults to True.
        """
        # Initialize module.
        super(QNetwork, self).__init__()
        
        # Initialize logger.
        self.__logger__:    Logger =    get_child("q-network")
        
        # Ensure that action space is discrete.
        assert isinstance(action_space, Discrete), f"Expected discrete action space, got {action_space}"
        
        # Create Q-network.
        self._network_:     Sequential =    Sequential(*create_mlp(
                                                input_size =    extract_space_size(space = observation_space),
                                                output_size =   action_space.n,
                                                hidden_size =   hidden_size,
                                                activation =    activation,
                                                squash_output = squash_output,
                                                bias =          bias,
                                                device =        device,
                                                data_type =     data_type
                                            ))
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized ({locals()})")
        
    # METHODS ======================================================================================
    
    def forward(self,
        observation:    Union[NDArray, Tensor]
    ) -> Tensor:
        """# Forward Pass through Q-Network.
        
        Provide Q-value(s) for observation(s).

        ## Args:
            * observation   (NDArray | Tensor): Environment observation(s).

        ## Returns:
            * Tensor:   Q-value(s) predicted for observation(s).
        """
        # Provide Q-value(s).
        return self._network_(observation)
    
    def predict_action(self,
        observation:    Union[NDArray, Tensor]
    ) -> Tensor:
        """# Predict Action.
        
        Predict the action(s) of provided observation(s) by taking the argmax of Q-value(s).

        ## Args:
            * observation   (NDArray | Tensor): Environment observation(s).

        ## Returns:
            * Tensor:   Action(s) predicted for observation(s).
        """
        # Predict action(s).
        return self._network_(observation).argmax(dim = 1).reshape(-1)