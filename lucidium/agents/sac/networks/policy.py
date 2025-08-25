"""# lucidium.agents.sac.networks.policy

Stochastic policy network for Soft Actor-Critic.
"""

__all__ = ["PolicyNetwork"]

from logging                import Logger
from typing                 import Callable, Tuple

from numpy                  import log as np_log
from numpy.typing           import NDArray
from torch                  import clamp, device, FloatTensor, log, tanh, Tensor
from torch.distributions    import Normal
from torch.nn               import Linear, Module
from torch.nn.functional    import relu

from lucidium.utilities     import get_child

class PolicyNetwork(Module):
    """# Policy Network
    
    Stochastic policy network π_φ(a | s) for continuous actions.

    The network outputs the mean and (log) standard deviation parameters of a diagonal Gaussian 
    policy. Actions are sampled via the reparameterization trick and squashed with tanh to enforce 
    bounds in (-1, 1) per action dimension.

    Notes:
        * Output distribution is N(mean, diag(std^2)), where std = exp(log_std).
        * Squashing (tanh) is applied in `sample(...)`, not in `forward(...)`.
        * If your environment expects actions in ranges other than (-1, 1), scale
          externally after sampling.
    """
    
    def __init__(self,
        state_dimension:    int,
        action_dimension:   int,
        hidden_dimension:   int =       256,
        log_std_lower:      float =     -20.0,
        log_std_upper:      float =     2.0,
        activation:         Callable =  relu,
        initial_weight:     float =     3e-3,
        to_device:          device =    device("cpu")
    ):
        """# Instantiate Policy Network.

        ## Args:
            * state_dimension   (int):      Size of the flattened input state vector.
            * action_dimension  (int):      Number of action dimensions (continuous control).
            * hidden_dimension  (int):      Width of the two hidden layers. Defaults to 256.
            * log_std_lower     (float):    Lower clamp for log standard deviation. Defaults to 
                                            -20.0.
            * log_std_upper     (float):    Upper clamp for log standard deviation. Defaults to 2.0.
            * activation        (Callable): Activation functino to use in network. Defaults to relu.
            * initial_weight    (float):    Value used to initialize weights of output layer. 
                                            Defaults to 0.003.
            * to_device         (device):   Device on which tensors will be placed. Defaults to CPU.
        """
        # Initialize module.
        super(PolicyNetwork, self).__init__()
        
        # Initialize logger.
        self.__logger__:        Logger =    get_child("policy")
        
        # Assign device.
        self._device_:          device =    to_device
        
        # Define action parameters.
        self._action_range_:    float =     10.0
        self._action_quantity_: int =       action_dimension
        
        # Define log standard deviation range to avoid numerical issues (vanishing/exploding STD).
        self._log_std_lower_:   float =     log_std_lower
        self._log_std_upper_:   float =     log_std_upper
        
        # Define layers.
        self._linear_1_:        Linear =    Linear(in_features = state_dimension,   out_features = hidden_dimension)
        self._linear_2_:        Linear =    Linear(in_features = hidden_dimension,  out_features = hidden_dimension)
        self._linear_3_:        Linear =    Linear(in_features = hidden_dimension,  out_features = hidden_dimension)
        self._linear_4_:        Linear =    Linear(in_features = hidden_dimension,  out_features = hidden_dimension)
        
        # Define heads for Gaussian parameters.
        self._mean_linear_:     Linear =    Linear(in_features = hidden_dimension,  out_features = action_dimension)
        self._log_std_linear_:  Linear =    Linear(in_features = hidden_dimension,  out_features = action_dimension)
        
        # Define activation function.
        self._activation_:  Callable =  activation
        
        # Initialize weights.
        self._mean_linear_.weight.data.uniform_(   -initial_weight, initial_weight)
        self._mean_linear_.bias.data.uniform_(     -initial_weight, initial_weight)
        self._log_std_linear_.weight.data.uniform_(-initial_weight, initial_weight)
        self._log_std_linear_.bias.data.uniform_(  -initial_weight, initial_weight)
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized Policy network ({locals()})")
        
    # METHODS ======================================================================================
    
    def evaluate(self,
        state:      Tensor,
        deterministic:  bool =  False,
        epsilon:        float = 1e-6
    ) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
        """# Evaluate Policy.

        ## Args:
            * state         (Tensor):   Environment state on which policy will be evaluated.
            * deterministic (bool):     If True, use the mean action (greedy). If False, sample with 
                                        reparameterization for low-variance gradients. Defaults to 
                                        False.
            * epsilon       (float):    Small constant to stabilize. Defaults to 1e-6.

        ## Returns:
            * action:           Tensor [B, act_dim] - final action in environment scale.
            * log_probability:  Tensor [B, 1] - log π(a | s) for the *sampled* action (or the mean 
                                action if deterministic=True).
            * noise:            Tensor [B, act_dim] - standard Normal noise used (zeros if 
                                deterministic).
            * mean:             Tensor [B, act_dim] - Gaussian mean before tanh.
            * log_std:          Tensor [B, act_dim] - Gaussian log std before tanh.
        """
        # Forward pass through network.
        mean, log_std =         self.forward(state)
        
        # Compute log standard deviation.
        std:        Tensor =    log_std.exp()
        
        # Generate noise.
        noise:      Tensor =    Normal(0, 1).sample(mean.shape)
        
        # Reparameterization trick with tanh squashing.
        action_0:   Tensor =    tanh(mean + std * noise.to(mean.device))
        action:     Tensor =    self._action_range_ * action_0
        
        # Compute log probability with tanh correction.
        log_prob:   Tensor =    (
                                    Normal(mean, std).log_prob(
                                        mean + 
                                        (std * noise.to(mean.device) if not deterministic else 0)
                                    ) - 
                                    log(1.0 - action_0.pow(2) + epsilon) - 
                                    np_log(self._action_range_)
                                ).sum(dim = -1, keepdim = True)
        
        # Provide results.
        return action, log_prob, noise, mean, log_std
    
    def forward(self,
        state:  Tensor
    ) -> Tuple[Tensor, Tensor]:
        """# Forward Pass Through Network.

        Compute Gaussian policy parameters for a batch of states.

        ## Args:
            * state (Tensor):   State tensor.

        ## Returns:
            * mean:     Tensor of shape (B, action_dim)
            * log_std:  Tensor of shape (B, action_dim), clamped to [log_std_min, log_std_max]

        ## Notes:
            * ReLU activations in hidden layers.
            * No activation on the heads; log_std is clamped explicitly.
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
        
        # Pass through third layer.
        X:  Tensor =    self._activation_(self._linear_3_(X))
        
        # Debug layer 3 output shape.
        self.__logger__.debug(f"Layer 3 output shape: {X.shape}")
        
        # Pass through fourth layer.
        X:  Tensor =    self._activation_(self._linear_4_(X))
        
        # Debug layer 4 output shape.
        self.__logger__.debug(f"Layer 4 output shape: {X.shape}")
        
        # Provide mean and standard deviation tensors.
        return  (
                    # Mean
                    self._mean_linear_(X),
                    
                    # Clamped standard deviation.
                    clamp(
                        input = self._log_std_linear_(X),
                        min =   self._log_std_lower_,
                        max =   self._log_std_upper_
                    )
                )
    
    def get_action(self,
        state:          Tensor,
        deterministic:  bool =  False
    ) -> NDArray:
        """# Get Action.
        
        Compute an action from the policy network given the current state.

        ## Args:
            * state         (Tensor):   Current environment state (observation).
            * deterministic (bool): 
                * If True: return the mean action (greedy, no exploration).
                * If False: sample a stochastic action using the reparameterization trick.

        ## Returns:
            NDArray:    Chosen action, clipped/scaled to valid range.
        """
        # Convert state to tensor and add batch dimension.
        state:  Tensor =    FloatTensor(state).unsqueeze(0).to(self._device_)
        
        # Forward pass through network.
        mean, log_std =     self.forward(state)
        
        # Compute standard deviation.
        std:    Tensor =    log_std.exp()
        
        # If deterministic, provide mean action.
        if deterministic: return tanh(mean).detach().cpu().numpy()[0]
        
        # Generate noise.
        noise:  Tensor =    Normal(0, 1).sample(mean.shape).to(self._device_)
        
        # Scale by standard deviation.
        action: Tensor =    self._action_range_ * tanh(mean + std * noise)
        
        # Provide shifted action.
        return action.detach().cpu().numpy().flatten()
    
    def sample_action(self) -> NDArray:
        """# Sample Action.
        
        Sample a completely random action (for exploration/initial replay filling).

        ## Returns:
            * NDArray:  Random action uniformaly sampled from [-action_range, +action_range].
        """
        return  (
            self._action_range_ *
            FloatTensor(self._action_quantity_).uniform_(-1, 1)
        ).numpy().flatten()