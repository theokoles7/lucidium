"""# lucidium.agents.dqn.base

Implementation of Deep Q-Network (DQN) agent based on "Playing Atari with Deep Reinforcement 
Learning" by Mnih et al. (2013).
Link to paper: https://arxiv.org/pdf/1312.5602
"""

__all__ = ["DeepQNetwork"]

from logging                        import Logger
from typing                         import Any, Dict, Literal, Optional, override

from numpy.random                   import rand
from torch                          import argmax, as_tensor, float32, load, long, manual_seed, no_grad, save, Tensor
from torch.nn                       import Module
from torch.nn.functional            import smooth_l1_loss
from torch.optim                    import Adam

from lucidium.agents.__base__       import Agent
from lucidium.agents.components     import QNetwork
from lucidium.agents.dqn.__args__   import register_dqn_parser
from lucidium.agents.dqn.__main__   import main
from lucidium.memory.replay         import ExperienceReplayBuffer
from lucidium.registries            import register_agent
from lucidium.spaces                import Space
from lucidium.utilities             import get_child

@register_agent(
    name =          "dqn",
    tags =          ["model-free", "gradient-free", "off-policy", "deep-rl"],
    entry_point =   main,
    parser =        register_dqn_parser
)
class DeepQNetwork(Agent):
    """# Deep Q-Network (DQN) Agent.
    
    Deep Q-Network is an off-policy, model-free reinforcement learning agent that utilizes a deep 
    neural network.
    
    Deep Q-Network (DQN) is a reinforcement learning agent that combines Q-learning with deep neural
    networks to enable agents to learn optimal policies directly from high-dimensional sensory 
    inputs.
    """
    
    def __init__(self,
        # Environment.
        action_space:           Space,
        observation_space:      Space,
        
        # Hyperparameters.
        learning_rate:          float =                             1e-3,
        discount_rate:          float =                             0.99,   # (gamma)
        exploration_rate:       float =                             1.0,    # (epsilon)
        exploration_decay:      float =                             0.99,
        exploration_min:        float =                             0.1,
        target_tau:             float =                             2e-3,
        update_interval:        int =                               4,
        
        # Experience Replay Buffer.
        replay_buffer_capacity: int =                               1e6,
        buffer_batch_size:      int =                               64,
        replay_policy:          Literal["prioritized", "uniform"] = "uniform",
        reaply_policy_kwargs:   Dict[str, Any] =                    None,
        
        # Seeding.
        random_seed:            int =                               42,
        to_device:              str =                               "cpu",
        **kwargs
    ):
        """# Instantiate Deep Q-Network Agent.

        ## Args:
            * action_space              (Space):    Environment's action space.
            * observation_space         (Space):    Environment's observation space.
            * learning_rate             (float):    Optimizer learning rate. Defaults to 1e-3.
            * discount_rate             (float):    Discount factor for action updates. Defaults to 
                                                    0.99.
            * exploration_rate          (float):    Probability that agent will choose to explore. 
                                                    Defaults to 1.0.
            * exploration_decay         (float):    Rate at which agent's exploration probability 
                                                    will decay. Defaults to 0.99.
            * exploration_min           (float):    Minimum value allowed for exploration rate. 
                                                    Defaults to 0.1.
            * target_tau                (float):    Soft update rate. Defaults to 0.002.
            * update_interval           (int):      Interval by which learning updates will occur. 
                                                    Defaults to 4.
            * replay_buffer_capacity    (int):      Maximum capacity for experience replay buffer. 
                                                    Defaults to 1e6.
            * buffer_batch_size         (int):      Size of batch samples from experience replay 
                                                    buffer. Defaults to 64.
            * random_seed               (int):      Random seed value for reproducibility. Defaults 
                                                    to 42.
            * to_device                 (str):      Device on which to run the agent. Defaults to 
                                                    "cpu".
        """
        # Initialize logger.
        self.__logger__:    Logger =    get_child("dqn")
        
        # Define environment components.
        self._action_space_:        Space =                     action_space
        self._observation_space_:   Space =                     observation_space
        
        # Define learning parameters.
        self._learning_rate_:       float =                     learning_rate
        
        # Define discount parameters.
        self._discount_rate_:       float =                     discount_rate
        
        # Define exploration parameters.
        self._exploration_rate_:    float =                     exploration_rate
        self._exploration_decay_:   float =                     exploration_decay
        self._exploration_min_:     float =                     exploration_min
        
        # Define soft update parameters.
        self._target_tau_:          float =                     target_tau
        self._update_interval_:     int =                       update_interval
        
        # Initialize experience replay buffer.
        self._replay_buffer_:       ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                                    capacity =      replay_buffer_capacity,
                                                                    batch_size =    buffer_batch_size,
                                                                    policy =        replay_policy,
                                                                    **(reaply_policy_kwargs or {})
                                                                )
        
        # Define networks.
        self._q_network_:           QNetwork =                  QNetwork(
                                                                    observation_size =  observation_space.n,
                                                                    action_size =       action_space.n,
                                                                    random_seed =       random_seed
                                                                ).to(to_device)
        
        # Define networks.
        self._target_q_network_:    QNetwork =                  QNetwork(
                                                                    observation_size =  observation_space.n,
                                                                    action_size =       action_space.n,
                                                                    random_seed =       random_seed
                                                                ).to(to_device)
        
        # Hard sync target network.
        self._target_q_network_.load_state_dict(state_dict = self._q_network_.state_dict())
        
        # Define optimizer.
        self._optimizer_:           Adam =                      Adam(
                                                                    params =    self._q_network_.parameters(),
                                                                    lr =        learning_rate
                                                                )
        
        # Define device on which to place tensors.
        self._device_:              str =                       to_device
        
        # Initialize step tracking.
        self._step_t_:              int =                       0
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized Deep Q-Network agent ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @property
    def name(self) -> str:
        """# DQN Agent Name.
        
        Deep Q-Network agent's proper name.
        """
        return "Deep Q-Network"
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """# DQN Statistics.
        
        Running statistics pertaining to agent's learning/performance.
        """
        return  {}
        
    # METHODS ======================================================================================
    
    @override
    def act(self,
        state:  Tensor
    ) -> int:
        """# Select Action.

        ## Args:
            * state (NDArray):  Current state of environment.

        ## Returns:
            * int:  Agent's chosen action.
        """
        # Cache current state.
        self._current_state_:   int =   state
        
        # If exploration rate (epsilon) is higher than a randomly chosen value...
        if rand() < self._exploration_rate_:
            
            # Log for debugging.
            self.__logger__.debug("Choosing to explore")
            
            # Explore.
            self._current_action_:  int =   self._action_space_.sample()
        
        # Otherwise...
        else:
            
            # Convert state to Tensor.
            if not isinstance(state, Tensor): state = as_tensor(state, dtype = float32)
            
            # Ensure batch dimension.
            if state.dim() == 0: state = state.view(1, 1)
            if state.dim() == 1: state = state.unsqueeze(0)
            
            # With no gradient update...
            with no_grad():
            
                # Log for debugging.
                self.__logger__.debug(f"Choosing best action for state {state}")
                
                # Choose max-value action from Q-table based on current state.
                self._current_action_:  int =   int(argmax(
                                                    self._q_network_(state.to(self._device_).float()),
                                                    dim = 1
                                                ).item())
            
        # Log for debugging.
        self.__logger__.debug(f"Chose action {self._current_action_} for state {state}")
            
        # Submit chosen action.
        return self._current_action_
    
    def load_model(self,
        path:   str
    ) -> None:
        """# Load Model.
        
        Load agent's network parameters from file.
        
        ## Args:
            * path (str):   File path to load model from.
        """
        # Load checkpoint file.
        checkpoint: Dict =  load(path, map_location = self._device_)
        
        # Load networks.
        self._q_network_.load_state_dict(checkpoint["q_network"])
        self._target_q_network_.load_state_dict(checkpoint["target_q_network"])
        
        # Load optimizer if it was saved.
        if "optimizer" in checkpoint: self._optimizer_.load_state_dict(checkpoint["optimizer"])
        
        # Otherwise, warn that it was not found.
        else: self.__logger__.warning(f"Checkpoint file {path} does not contain optimizer")
        
        # Load time step.
        self._step_t_ = int(checkpoint.get("step", 0))
        
        # Log for debugging.
        self.__logger__.info(f"Loaded model from {path}")
        
    @override
    def observe(self,
        new_state:  Tensor,
        reward:     float,
        done:       bool
    ) -> Dict[str, float]:
        """# Observe Transition

        ## Args:
            * new_state (Tensor):   State of environment after agent's action.
            * reward    (float):    Reward yielded/penalty incurred by agent's action.
            * done      (bool):     Flag indicating if new state is terminal.

        ## Returns:
            * Dict[str, float]: Agent's observation metrics.
        """
        # Debug transition observation.
        self.__logger__.debug(f"Observing transition [old_state: {self._current_state_}, action: {self._current_action_}, reward: {reward}, new_state: {new_state}, done: {done}]")
        
        # Commit transition experience to memory.
        self._replay_buffer_.push(self._current_state_, self._current_action_, reward, new_state, done)
        
        # Increment step tracker.
        self._step_t_                            += 1
        
        # Initialize observation metrics map.
        observation_metrics:    Dict[str, float] =  {
                                                        "loss":             None,
                                                        "exploration_rate": None
                                                    }
        
        # If this is an update interval...
        if self._step_t_ % self._update_interval_ == 0:
            
            # Update target and compute loss.
            loss:   float = self._update_()
            
            # If loss was computed...
            if loss is not None:
                
                # Record loss.
                self._last_loss_:   float = float(loss)
                
                # Update observation metrics.
                observation_metrics["loss"] = self._last_loss_
                
        # Decay ecploration rate (epsilon).
        self._exploration_rate_:    float = max(
                                                self._exploration_min_,
                                                self._exploration_rate_ * self._exploration_decay_
                                            )
        
        # Update observation metrics.
        observation_metrics["exploration_rate"] = self._exploration_rate_
        
        # Provide observatino metrics.
        return  observation_metrics
    
    def save_model(self,
        path:   str
    ) -> None:
        """# Save Model.
        
        Save agent's network parameters to file.
        
        ## Args:
            * path (str):   Path at which agent's model will be written.
        """
        # Save model to file.
        save(
            {
                "q_network":        self._q_network_.state_dict(),
                "target_q_network": self._target_q_network_.state_dict(),
                "optimizer":        self._optimizer_.state_dict(),
                "step":             self._step_t_
            },
            path
        )
        
        # Log for debugging.
        self.__logger__.info(f"Saved model fto {path}")
        
    # HELPERS ======================================================================================
    
    def _seed_(self,
        random_seed:    int
    ) -> None:
        """# Seed Deep Q-Network Agent.
        
        Set the random seed so that initialization and stochastic operations are reproducible.

        ## Args:
            * random_seed   (int):  Random seed.
        """
        # Set the seed for generating random numbers on all devices.
        manual_seed(seed = random_seed)
        
        # Debug seed.
        self.__logger__.debug(f"Seeded Deep Q-Network with seed = {random_seed}")
    
    @staticmethod
    def _soft_update_(
        target_network: Module,
        online_network: Module,
        tau:            float
    ) -> None:
        """# Soft-Update Target Network.
        
        Polyak averaging.

        ## Args:
            * target_network    (Module):   Target network.
            * online_network    (Module):   Online Q network.
            * tau               (float):    Soft update coefficient (polyak factor).
        """
        # With no gradient update...
        with no_grad():
            
            # For each parameter in each network...
            for target_parameter, paramter in zip(target_network.parameters(), online_network.parameters()):
                
                # Adminster Polyak averaging based on online network.
                target_parameter.data.mul_(1.0 - tau).add_(tau * paramter.data)
    
    def _update_(self) -> Optional[float]:
        """# Update Target Parameters.
        
        Sample fro replay buffer and update Q-Network.
        
        ## Returns:
            * float | None: Loss item if network was updated.
        """
        # If replay buffer is not ready for sampling, no update should be made.
        if not self._replay_buffer_.is_ready_for_sampling: return None
        
        # Sample a batch from experience replay buffer.
        old_states, actions, rewards, new_states, dones = self._replay_buffer_.sample()
        
        # Convert to Tensors.
        old_states: Tensor =    as_tensor(old_states, device = self._device_, dtype = float32)
        actions:    Tensor =    as_tensor(actions,    device = self._device_, dtype = long).view(-1, 1)
        rewards:    Tensor =    as_tensor(rewards,    device = self._device_, dtype = float32).view(-1)
        new_states: Tensor =    as_tensor(new_states, device = self._device_, dtype = float32)
        dones:      Tensor =    as_tensor(dones,      device = self._device_, dtype = float32).view(-1)
        
        # Get Q(s, a) from online network.
        q_sa:       Tensor =    self._q_network_(old_states).gather(1, actions).squeeze(1)
        
        # With no gradient udpate...
        with no_grad():
            
            # Get max value from target network.
            q_max:  Tensor =    self._target_q_network_(new_states).max(dim = 1).values
            
            # Compute bootstrap target.
            y:      Tensor =    rewards + self._discount_rate_ * (1.0 - dones) * q_max
            
        # Compute Huber loss between current Q and target.
        loss:       Tensor =    smooth_l1_loss(input = q_sa, target = y)
        
        # Reset gradients.
        self._optimizer_.zero_grad(set_to_none = True)
        
        # Back propagation.
        loss.backward()
        
        # Update weights.
        self._optimizer_.step()
        
        # Soft update target network.
        self._soft_update_(
            target_network =    self._target_q_network_,
            online_network =    self._q_network_,
            tau =               self._target_tau_
        )
        
        # Provide computed loss.
        return float(loss.item())