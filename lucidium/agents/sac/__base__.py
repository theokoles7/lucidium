"""# lucidium.agents.sac.base

Implementation of Soft Actor-Critic, based on "Soft Actor-Critic: Off-Policy Maximum Entropy Deep 
Reinforcement Learning with a Stochastic Actor", by Haarnoja et. al. (2018).

Link to paper: https://proceedings.mlr.press/v80/haarnoja18b/haarnoja18b.pdf
"""

__all__ = ["SoftActorCritic"]

from logging                            import Logger
from typing                             import Any, Dict, List, Literal, override, Optional

from numpy                              import array, float32, ndarray
from numpy.typing                       import NDArray
from torch                              import cuda, device, FloatTensor, load, min, no_grad, save, stack, Tensor, zeros
from torch.nn                           import MSELoss
from torch.nn.functional                import relu
from torch.optim                        import Adam

from lucidium.agents.__base__           import Agent
from lucidium.agents.sac.__args__       import register_sac_parser
from lucidium.agents.sac.__main__       import main
from lucidium.agents.sac.networks       import *
from lucidium.agents.sac.replay_buffer  import ExperienceReplayBuffer
from lucidium.registries                import register_agent
from lucidium.spaces                    import Space
from lucidium.utilities                 import get_child

@register_agent(
    name =          "sac",
    tags =          ["model-free", "off-policy", "actor-critic", "maximum-entropy", "continuous-control"],
    entry_point =   main,
    parser =        register_sac_parser
)
class SoftActorCritic(Agent):
    """# Soft Actor-Critic (Agent)

    Implementation of Soft Actor-Critic, based on "Soft Actor-Critic: Off-Policy Maximum Entropy 
    Deep Reinforcement Learning with a Stochastic Actor", by Haarnoja et. al. (2018).

    Link to paper: https://proceedings.mlr.press/v80/haarnoja18b/haarnoja18b.pdf
    """
    
    def __init__(self,
        # Environment parameters.
        action_space:               Space,
        observation_space:          Space,
        
        # Network dimensions.
        actor_hidden_dimension:     int =                           512,
        critic_hidden_dimension:    int =                           512, 
        value_hidden_dimension:     int =                           512,
        
        # Learning.
        actor_lr:                   float =                         3e-4,
        critic_lr:                  float =                         3e-4,
        value_lr:                   float =                         3e-4,
        
        # Observation parameters.
        discount_rate:              float =                         0.99,
        soft_update_coefficient:    float =                         1e-2,
        temperature:                float =                         1.0,
        auto_temperature:           bool =                          False,
        target_entropy:             Optional[float] =               None,
        
        # Experience replay buffer.
        buffer_size:                int =                           1000000,
        batch_size:                 int =                           128,
        gradient_steps:             int =                           1,
        exploration_steps:          int =                           0,
        reward_scale:               float =                         10.0,
        
        # Hardware optimization.
        to_device:                  str =                           "auto",
        
        **kwargs
    ):
        """# Instantiate Soft Actor-Critic (Agent).

        ## Environment Args:
            * action_space              (Space):            Action space of environment.
            * observation_space         (Space):            Observation space of environment.
            
        ## Network Dimensions:
            * actor_hidden_dimension    (List[int]):        Size of actor network's hidden layer. 
                                                            Defaults to 512.
            * critic_hidden_dimension   (List[int]):        Size of critic network's hidden layer. 
                                                            Defaults to 512.
            * value_hidden_dimension    (List[int]):        Size of value network's hidden layer. 
                                                            Defaults to 512.
                                                            
        ## Learning Rates:
            * actor_lr                  (float):            Learning rate of actor network. Defaults 
                                                            to 3e-4.
            * critic_lr                 (float):            Learning rate of critic network. 
                                                            Defaults to 3e-4.
            * value_lr                  (float):            Learning rate of value network. Defaults 
                                                            to 3e-4.
                
        ## Observation Parameters:
            * discount_rate             (float):            Discount factor for expected action 
                                                            rewards. Defaults to 0.99.
            * soft_update_coefficient   (float):            Soft update coefficient (tau). Defaults 
                                                            to 1e-2.
            * temperature               (float):            Temerature parameter (alpha). Defaults 
                                                            to 1.0.
            * auto_temperature          (bool):             If true, temperature will be auto-tuned. 
                                                            Defaults to False.
            * target_entropy            (Optional[float]):  Target entropy for auto temperature 
                                                            tuning. Defaults to None.
                                                            
        ## Experience Replay Buffer:
            * buffer_size               (int):              Maximum capacity of experience replay 
                                                            buffer. Defaults to 1000000.
            * batch_size                (int):              Training batch size. Defaults to 128.
            * gradient_steps            (int):              Gradient steps per environment 
                                                            interaction. Defaults to 1.
            * exploration_steps         (int):              Number of steps for which agent should 
                                                            focus on exploring before acting from 
                                                            policy. Defaults to 0.
            * reward_scale              (float):            Reward scaling factor. Defaults to 10.0.
            
        ## CAR (Conservative Advantage Regularization):
            * car_enabled               (bool):             If true, conservative advantage 
                                                            regularization will be utilized for 
                                                            actor (policy) network. Defaults to 
                                                            False.
            * car_lambda                (float):            CAR penalty coefficient. Defaults to 
                                                            0.0003.
            * car_mode                  (str):              Either "batch" or "per_state". Defaults 
                                                            to "per_state".
            * car_k                     (int):              If "per_state', then k actions will be 
                                                            sampled per state. Defaults to 5.
            
        ## Hardware Optimization:
            * to_device                 (str):              Device to use. Defaults to "auto".
        """
        # Initialize logger.
        self.__logger__:                Logger =                    get_child("sac")
        
        # Define device.
        self._device_:                  device =                    to_device if to_device != "auto" \
                                                                    else ("cuda" if cuda.is_available() else "cpu")
        
        # Define environment spaces.
        self._action_space_:            Space =                     action_space
        self._observation_space_:       Space =                     observation_space
        
        # Extract action and state dimensions.
        self._action_dimension_:        int =                       self._action_space_.shape[0]
        self._state_dimension_:         int =                       self._observation_space_.shape[0]
        
        # Define hyperparameters.
        self._discount_rate_:           float =                     discount_rate
        self._soft_update_coefficient_: float =                     soft_update_coefficient
        self._temperature_:             float =                     temperature
        self._batch_size_:              int =                       batch_size
        self._gradient_steps_:          int =                       gradient_steps
        self._exploration_steps_:       int =                       exploration_steps
        self._reward_scale_:            float =                     reward_scale
        
        # Initialize networks.
        self._actor_:                   PolicyNetwork =             PolicyNetwork(
                                                                        state_dimension =   self._state_dimension_,
                                                                        action_dimension =  self._action_dimension_,
                                                                        hidden_dimension =  actor_hidden_dimension,
                                                                        activation =        relu
                                                                    ).to(self._device_)
        
        self._critic_1_:                SoftQNetwork =              SoftQNetwork(
                                                                        state_dimension =   self._state_dimension_,
                                                                        action_dimension =  self._action_dimension_,
                                                                        hidden_dimension =  critic_hidden_dimension,
                                                                        activation =        relu
                                                                    ).to(self._device_)
        
        self._critic_2_:                SoftQNetwork =              SoftQNetwork(
                                                                        state_dimension =   self._state_dimension_,
                                                                        action_dimension =  self._action_dimension_,
                                                                        hidden_dimension =  critic_hidden_dimension,
                                                                        activation =        relu
                                                                    ).to(self._device_)
        
        self._value_network_:           ValueNetwork =              ValueNetwork(
                                                                        state_dimension =   self._state_dimension_,
                                                                        hidden_dimension =  value_hidden_dimension,
                                                                        activation =        relu
                                                                    ).to(self._device_)
        
        self._target_value_network_:    ValueNetwork =              ValueNetwork(
                                                                        state_dimension =   self._state_dimension_,
                                                                        hidden_dimension =  value_hidden_dimension,
                                                                        activation =        relu
                                                                    ).to(self._device_)
        
        # Initialize target network with main network weights.
        for target_parameter, parameter in zip(
            self._target_value_network_.parameters(),
            self._value_network_.parameters()
        ):
            target_parameter.data.copy_(parameter.data)
            
        # Define loss functions.
        self._value_loss_:              MSELoss =                   MSELoss()
        self._critic_1_loss_:           MSELoss =                   MSELoss()
        self._critic_2_loss_:           MSELoss =                   MSELoss()
        
        # Define optimizers.
        self._actor_optimizer_:         Adam =                      Adam(params = self._actor_.parameters(),         lr = actor_lr)
        self._critic_1_optimizer_:      Adam =                      Adam(params = self._critic_1_.parameters(),      lr = critic_lr)
        self._critic_2_optimizer_:      Adam =                      Adam(params = self._critic_2_.parameters(),      lr = critic_lr)
        self._value_optimizer_:         Adam =                      Adam(params = self._value_network_.parameters(), lr = value_lr)
        
        # Initialize experience replay buffer.
        self._replay_buffer_:           ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                                        capacity =      buffer_size,
                                                                        batch_size =    batch_size,
                                                                        to_device =     self._device_
                                                                    )
        
        # Initialize training state.
        self._frame_index_:             int =                       0
        self._last_state_:              Any =                       None
        self._last_action_:             Any =                       None
        
        # Initialize statistics.
        self._episode_reward_:          float =                     0.0
        self._episode_length_:          int =                       0
        
        # Log initialization for debugging.
        self.__logger__.debug(f"Initialized SAC agent ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def name(self) -> str:
        """# (SAC) Name

        SAC agent's proper name.
        """
        return "Soft Actor-Critic"
    
    @override
    @property
    def statistics(self) -> Dict[str, Any]:
        """# (SAC) Statistics

        Statistics pertaining to SAC performance/status.
        """
        return  {
                    "frame_index":              self._frame_index_,
                    "buffer_size":              len(self._replay_buffer_),
                    "temperature":              self._temperature_,
                    "episode_reward":           self._episode_reward_,
                    "episode_length":           self._episode_length_,
                    "discount_rate":            self._discount_rate_,
                    "soft_update_coefficient":  self._soft_update_coefficient_,
                    "batch_size":               self._batch_size_,
                    "reward_scale":             self._reward_scale_
                }
        
    # METHODS ======================================================================================
    
    @override
    def act(self,
        state:  Any
    ) -> Any:
        """# Select Action.
        
        Choose action based on current state using current policy (actor).

        ## Args:
            * state (Any):  Current state observation.

        ## Returns:
            * Any:  Agent's chosen action.
        """
        # Debug state.
        self.__logger__.debug(f"Acting on state {state}")
        
        # Ensure state is in proper format.
        if not isinstance(state, ndarray): state = array(state, dtype = float32)
        
        # Ensure state is in one dimension.
        if state.ndim > 1: state = state.flatten()
        
        # Store for next observation.
        self._last_state_:  ndarray =   state.copy()
        
        # If exploration steps are completed...
        if self._frame_index_ >= self._exploration_steps_:
            
            # Then with no gradient updates...
            with no_grad():
                
                # Act on policy.
                action: ndarray =   self._actor_.get_action(
                                        state =         FloatTensor(state).unsqueeze(0).to(self._device_),
                                        deterministic = False
                                    )
                
        # Otherwise...
        else:
            
            # Continue exploration.
            action:     ndarray =   self._actor_.sample_action()
            
        # Store for next observation.
        self._last_action_: ndarray =   action.copy()
        
        # Submit action.
        return action
    
    @override
    def load_model(self,
        path:   str
    ) -> None:
        """# Load Model.
        
        Load agent's networks from file.

        ## Args:
            * path  (str):  Path at which model will be loaded.
        """
        # Load checkpoint file.
        checkpoint: Dict =  load(f = open(path, "r"), map_location = self._device_)
        
        # Load model states.
        self._actor_.load_state_dict(checkpoint["actor"])
        self._value_network_.load_state_dict(checkpoint["value"])
        self._target_value_network_.load_state_dict(checkpoint["target_value"])
        self._critic_1_.load_state_dict(checkpoint["critic_1"])
        self._critic_2_.load_state_dict(checkpoint["critic_2"])
        
        # Log for debugging.
        self.__logger__.info(f"Loaded SAC models from {path}")
    
    @override
    def observe(self,
        new_state:  Any,
        reward:     float,
        done:       bool
    ) -> Dict[str, Any]:
        """# Observe.
        
        Observe transition and update agent.

        ## Args:
            * new_state (Any):      State of environment after action was submitted.
            * reward    (float):    Reward yielded/penalty incurred by action submitted to 
                                    environment.
            * done      (bool):     Flag indicating if new state is terminal.
            
        ## Returns:
            * Dict[str, float]: Agent's observation metrics.
        """
        # Update episode statistics.
        self._episode_reward_ += reward
        self._episode_length_ += 1
        
        # Ensure state is in proper format.
        if not isinstance(new_state, ndarray): new_state = array(new_state, dtype = float32)
        
        # Ensure state is in one dimension.
        if new_state.ndim > 1: new_state = new_state.flatten()
        
        # If there is a prior state & action recorded...
        if self._last_action_ is not None and self._last_state_ is not None:
            
            # Store transition.
            self._replay_buffer_.push(
                old_state = self._last_state_,
                action =    self._last_action_,
                reward =    reward,
                new_state = new_state,
                done =      done
            )
            
        # Increment frame index.
        self._frame_index_ += 1
        
        # Initialize storage of expected Q-value.
        q_value: float = 0.0
        
        # If we have enough samples to make a training batch...
        if self._replay_buffer_.read_for_training:
            
            # Train networks.
            for _ in range(self._gradient_steps_): q_value = self._update_()
                
        # If episode concluded...
        if done:
            
            # Reset statistics.
            self._episode_reward_:  float =     0.0
            self._episode_length_:  int =       0
            self._last_state_:      ndarray =   None
            self._last_action_:     ndarray =   None
            
        # Otherwise, simply update state for next step.
        else: self._last_state = new_state
        
        # Submit observation.
        return  {
                    "reward":               reward,
                    "done":                 done,
                    "frame_index":          self._frame_index_,
                    "buffer_size":          len(self._replay_buffer_),
                    "predicted_q_value":    q_value
                }
        
    @override
    def save_model(self,
        path:   str
    ) -> None:
        """# Save Model.
        
        Save agent's networks to file.

        ## Args:
            * path  (str):  Path at which agent's network models will be saved.
        """
        # Save model checkpoints.
        save(
            obj =   {
                        "actor":        self._actor_.state_dict(),
                        "value":        self._value_network_.state_dict(),
                        "target_value": self._target_value_network_.state_dict(),
                        "critic_1":     self._critic_1_.state_dict(),
                        "critic_2_":    self._critic_2_.state_dict()
                    },
            f =     path
        )
        
        # Log for debugging.
        self.__logger__.debug(f"Saved SAC models to {path}")
        
    # HELPERS ======================================================================================
    
    def _update_(self) -> float:
        """# Update Networks.
        
        Update networks based on current state/status.

        ## Returns:
            * float:    Mean predicated Q-value for monitoring.
        """
        # Saple a batch from experience replay buffer.
        batch:              Dict[str, Tensor] = self._replay_buffer_.sample()
        
        # Extract transition components.
        old_states:         Tensor =   batch["old_state"].to(self._device_)
        actions:            Tensor =   batch["action"].to(self._device_)
        rewards:            Tensor =   batch["reward"].to(self._device_)
        new_states:         Tensor =   batch["new_state"].to(self._device_)
        done:               Tensor =   batch["done"].to(self._device_)
        
        # Normalize rewards.
        rewards = self._reward_scale_ * (rewards - rewards.mean(0)) / (rewards.std(0) + 1e-6)
        
        # Get current Q-values and V-values.
        predicted_q_1:     Tensor =    self._critic_1_(old_states, actions)
        predicted_q_2:     Tensor =    self._critic_2_(old_states, actions)
        predicted_value:   Tensor =    self._value_network_(old_states)
        new_actions, log_probs, noise, means, log_stds = self._actor_.evaluate(old_states)
        
        # With no gradient updates...
        with no_grad():
            
            # Compute target Q-value.
            target_q_value: Tensor =    rewards + (1 - done) * self._discount_rate_ * self._target_value_network_(new_states)
            
        # Compute loss for critics.
        critic_1_loss:      Tensor =    self._critic_1_loss_(predicted_q_1, target_q_value)
        critic_2_loss:      Tensor =    self._critic_2_loss_(predicted_q_2, target_q_value)
        
        # Zero gradients.
        self._critic_1_optimizer_.zero_grad()
        self._critic_2_optimizer_.zero_grad()
        
        # Back propagation.
        critic_1_loss.backward()
        critic_2_loss.backward()
        
        # Update weights.
        self._critic_1_optimizer_.step()
        self._critic_2_optimizer_.step()
        
        # Make conservative estimate for new Q-value.
        new_q_value:        Tensor =    min(
                                            self._critic_1_(old_states, new_actions),
                                            self._critic_2_(old_states, new_actions)
                                        )
        
        # Compute target value function loss based on conservative critic estimate.
        value_loss:         Tensor =    self._value_loss_(
                                            predicted_value,
                                            (new_q_value - self._temperature_ * log_probs).detach()
                                        )
        
        # Zero gradients.
        self._value_optimizer_.zero_grad()
        
        # Back propagation.
        value_loss.backward()
        
        # Update weights.
        self._value_optimizer_.step()
        
        # Compute actor loss.
        actor_loss:         Tensor =    (self._temperature_ * log_probs - new_q_value).mean()
        
        # Zero gradients.
        self._actor_optimizer_.zero_grad()
        
        # Back propagation.
        actor_loss.backward()
        
        # Update weights.
        self._actor_optimizer_.step()
        
        # For each parameter in value networks...
        for target_parameter, parameter in zip(
            self._target_value_network_.parameters(),
            self._value_network_.parameters()
        ):
            # Perform soft-Q update.
            target_parameter.data.copy_(
                target_parameter.data * (
                    1.0 - self._soft_update_coefficient_
                ) + parameter.data * self._soft_update_coefficient_
            )
        
        # Provide new Q-value prediction.
        return new_q_value.mean().item()