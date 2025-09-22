"""# lucidium.agents.dqn.base

Implementation of Deep Q-Network (DQN) agent based on "Playing Atari with Deep Reinforcement 
Learning" by Mnih et al. (2013).
"""

__all__ = ["DQN"]

from itertools                      import count
from os                             import makedirs
from typing                         import Any, Dict, List, Literal, Optional, override, Union

from gymnasium                      import Env
from numpy                          import array, clip
from numpy.random                   import rand
from numpy.typing                   import NDArray
from torch                          import BoolTensor, device, FloatTensor, float32, load, long, LongTensor, no_grad, save, stack, tensor, Tensor
from torch.nn                       import Module
from torch.nn.functional            import smooth_l1_loss
from torch.nn.utils                 import clip_grad_value_
from torch.optim                    import Adam

from lucidium.agents.__base__       import Agent
from lucidium.agents.dqn.__args__   import register_dqn_parser
from lucidium.agents.dqn.__main__   import dqn_entry_point
from lucidium.memory                import ExperienceReplayBuffer, Transition
from lucidium.neural                import QNetwork
from lucidium.registration          import register_agent

@register_agent(
    name =          "dqn",
    tags =          ["model-free", "value-based", "off-policy", "deep-rl"],
    entry_point =   dqn_entry_point,
    parser =        register_dqn_parser
)
class DQN(Agent):
    """# Deep Q-Network (DQN) Agent.
    
    Deep Q-Network is an off-policy, model-free reinforcement learning agent that utilizes a deep 
    neural network.
    
    Deep Q-Network (DQN) is a reinforcement learning agent that combines Q-learning with deep neural
    networks to enable agents to learn optimal policies directly from high-dimensional sensory 
    inputs.
    """
    
    def __init__(self,
        # Environment.
        environment:                Env, *,
        
        # Exploration.
        exploration_rate:           float =                             1.0,
        exploration_decay:          float =                             0.995,
        exploration_min:            float =                             0.01,
        
        # Rewards.
        discount_rate:              float =                             0.99,
        clip_rewards:               bool =                              False,
        
        # Optimization.
        learning_rate:              float =                             2e-4,
        target_update_frequency:    int =                               100,
        
        # Experience Replay Buffer.
        buffer_capacity:            int =                               1e6,
        buffer_batch_size:          int =                               32,
        replay_policy:              Literal["prioritized", "uniform"] = "uniform",
        replay_policy_kwargs:       Dict[str, Any] =                    {},
        
        # Seeding & Hardware.
        random_seed:                int =                               42,
        to_device:                  str =                               "cpu",
        **kwargs
    ):
        """# Instantiate Deep Q-Network.

        ## Args:
            * environment               (Env):              Environment with which agent will 
                                                            interact.
                                                            
        ## Exploration:
            * exploration_rate          (float):            Initial exploration rate. Defaults to 
                                                            1.0.
            * exploration_decay         (float):            Rate at which exploration rate will 
                                                            decay. Defaults to 0.995.
            * exploration_min           (float):            Value at which exploration rate decay 
                                                            will cease. Defaults to 0.01.
                                                            
        ## Rewards:
            * discount_rate             (float):            Future reward discount factor. Defaults 
                                                            to 0.99.
            * clip_rewards              (bool):             If true, rewards will be clipped. 
                                                            Defaults to False.
        
        ## Optimization:
            * learning_rate             (float):            Optimizer learning rate. Defaults to 
                                                            2e-4.
            * target_update_frequency   (int):              Step interval at which target network 
                                                            parameters will be updated. Defaults to 
                                                            100.
                                                            
        ## Experience Replay:
            * buffer_capacity           (int):              Maximum capacity of experience replay 
                                                            buffer. Defaults to 1e6.
            * buffer_batch_size         (int):              Buffer sampling batch size. Defaults to 
                                                            32.
            * replay_policy             (str):              Policy that will dictate buffer 
                                                            sampling. Defaults to "uniform".
            * replay_policy_kwargs      (Dict[str, Any]):   Policy specific arguments map. Defaults 
                                                            to None.
                                                            
        ## Seeding & Hardware:
            * random_seed               (int):              Random seed value for reproducibility. 
                                                            Defaults to 42.
            * to_device                 (str):              Torch device upon which data will be 
                                                            placed. Defaults to "cpu".
        """
        # Initialize agent.
        super(DQN, self).__init__(id = "dqn", name = "Deep Q-Network", environment = environment, random_seed = random_seed)
        
        # Define exploration parameters.
        self._exploration_rate_:        float =                     float(exploration_rate)
        self._exploration_decay_:       float =                     float(exploration_decay)
        self._exploration_min_:         float =                     float(exploration_min)
        
        # Define reward handling.
        self._discount_rate_:           float =                     float(discount_rate)
        self._clip_rewards_:            bool =                      bool(clip_rewards)
        
        # Define optimization parameters.
        self._learning_rate_:           float =                     float(learning_rate)
        self._target_update_frequency_: int =                       int(target_update_frequency)
        
        # Initialize experience replay buffer.
        self._memory_:                  ExperienceReplayBuffer =    ExperienceReplayBuffer(
                                                                        capacity =      buffer_capacity,
                                                                        batch_size =    buffer_batch_size,
                                                                        policy =        replay_policy,
                                                                        **replay_policy_kwargs
                                                                    )
        
        # Define value network.
        self._value_:                   QNetwork =                  QNetwork(
                                                                        observation_space = self._environment_.observation_space,
                                                                        action_space =      self._environment_.action_space,
                                                                        device =            to_device
                                                                    )
        
        # Define target network.
        self._target_:                  QNetwork =                  QNetwork(
                                                                        observation_space = self._environment_.observation_space,
                                                                        action_space =      self._environment_.action_space,
                                                                        device =            to_device
                                                                    )
        
        # Hard sync target network to value network parameters.
        self._update_target_network_()
        
        # Define optimizer.
        self._optimizer_:               Adam =                      Adam(
                                                                        params =    self._value_.parameters(),
                                                                        lr =        self._learning_rate_
                                                                    )
        
        # Define device on which to place tensors.
        self._device_:                  str =                       device(to_device)
        
        # Initialize step tracking.
        self._steps_taken_:             int =                       0
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """# DQN Statistics.
        
        Running statistics pertaining to agent's learning/performance.
        """
        return  {
                    "step":             self._steps_taken_,
                    "exploration_rate": self._exploration_rate_,
                    "buffer_size":      self._memory_.size,
                    "buffer_ready":     self._memory_.is_ready_for_sampling
                }
        
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
        # If exploration rate (epsilon) is higher than a randomly chosen value...
        if rand() < self._exploration_rate_:
            
            # Explore.
            action: int =   self._explore_()
        
        # Otherwise...
        else:
            # Choose best action.
            action: int =   self._select_best_action_(state = state)
            
        # Debug action.
        self.__logger__.debug(f"Chose action {action} for state {state}")
            
        # Submit chosen action.
        return action
    
    @override
    def evaluate_episode(self) -> Dict[str, Any]:
        """# Evaluate Agent for One Episode.

        ## Returns:
            * Dict[str, Any]:   Evaluation statistics/results.
        """
        # Reset environment.
        state, info =   self._environment_.reset()
            
        # Convert state to tensor.
        state:  Tensor =    tensor(state, dtype = float32, device = self._device_).unsqueeze(0)
        
        # Initialize reward tracking.
        episode_reward: float = 0.0
        
        # Until environment is solved...
        for step in count():
            
            # Select an action.
            action:     int =                               self._select_best_action_(state = state)
            
            # Submit action.
            new_state, reward, terminal, truncated, meta =  self._environment_.step(action = action)
            
            # Track reward.
            episode_reward +=                               reward
            
            # Convert new state to tensor.
            new_state:  Tensor =                            tensor(
                                                                new_state,
                                                                dtype =     float32,
                                                                device =    self._device_
                                                            ).unsqueeze(0)
            
            # Episode concludes if new state is terminal/truncated.
            if terminal or truncated: break
            
            # Update current state.
            state =                                         new_state
            
        # Provide evaluation resutls.
        return {"reward": episode_reward, "steps": step}
    
    @override
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
        
        # Load checkpoint state dictionaries.
        self._value_.load_state_dict(checkpoint["value_network_state_dict"])
        self._target_.load_state_dict(checkpoint["target_network_state_dict"])
        self._optimizer_.load_state_dict(checkpoint["optimizer_state_dict"])
        
        # Load time step.
        self._steps_taken_: int =       int(checkpoint.get("step", 0))
        
        # Load hyperparameters.
        self._learning_rate_:           float = float(checkpoint.get("learning_rate",         2e-4))
        self._discount_rate_:           float = float(checkpoint.get("discount_rate",         0.99))
        self._exploration_rate_:        float = float(checkpoint.get("exploration_rate",      1.0))
        self._exploration_min_:         float = float(checkpoint.get("exploration_min",       0.01))
        self._exploration_decay_:       float = float(checkpoint.get("exploration_decay",     0.995))
        self._target_update_frequency_: int =   int(checkpoint.get("target_update_frequency", 10000))
        self._clip_rewards_:            bool =  bool(checkpoint.get("clip_rewards",           False))
        
        # Log for debugging.
        self.__logger__.info(f"Loaded model from {path}")
        
    @override
    def observe(self,
        state:      Tensor,
        action:     int,
        reward:     float,
        new_state:  Tensor,
        done:       bool
    ) -> float:
        """# Observe Transition

        ## Args:
            * state     (Tensor):   Initial state of environment before action was submitted.
            * action    (int):      Action submitted by agent.
            * reward    (float):    Reward yielded/penalty incurred by action submitted to 
                                    environment.
            * new_state (Tensor):   State of environment after action was submitted.
            * done      (bool):     Flag indicating if new state is terminal.

        ## Returns:
            * float:    Loss calculation.
        """
        # Debug transition observation.
        self.__logger__.debug(f"Observing transition [{state}, {action}, {reward}, {new_state}, {done}]")
        
        # Increment step tracker.
        self._steps_taken_ +=   1
        
        # Clip reward if requested.
        if self._clip_rewards_: reward = clip(reward, -1, 1)
        
        # Commit transition experience to memory.
        self._memory_.push(state, action, reward, new_state, done)
        
        # Train value network.
        loss:   float =         self._train_value_network_()
        
        # Update target network parameters if this is the proper interval.
        if self._steps_taken_ % self._target_update_frequency_ == 0: self._update_target_network_()
        
        # Decay epsilon.
        self._decay_epsilon_()
        
        # Provide loss calculation.
        return loss
    
    @override
    def save_model(self,
        path:   str
    ) -> None:
        """# Save Model.
        
        Save agent's network parameters to file.
        
        ## Args:
            * path (str):   Path at which agent's model will be written.
        """
        # Ensure path exists.
        makedirs(name = path, exist_ok = True)
        
        # Save model checkpoint to file.
        save(
            {
                "value_network_state_dict":     self._value_.state_dict(),
                "target_network_state_dict":    self._target_.state_dict(),
                "optimizer_state_dict":         self._optimizer_.state_dict(),
                "steps_taken":                  self._steps_taken_,
                "hyperparameters": {
                    "learning_rate":            self._learning_rate_,
                    "discount_rate":            self._discount_rate_,
                    "exploration_rate":         self._exploration_rate_,
                    "exploration_min":          self._exploration_min_,
                    "exploration_decay":        self._exploration_decay_,
                    "target_update_frequency":  self._target_update_frequency_,
                    "clip_rewards":             self._clip_rewards_
                }
            },
            f"{path}/agent_checkpoint.pth"
        )
        
        # Log for debugging.
        self.__logger__.info(f"Saved model to {path}")
        
    @override
    def train_episode(self) -> Dict[str, Any]:
        """# Train Agent for One Episode.

        ## Returns:
            * Dict[str, Any]:   Training statistics/results.
        """
        # Reset environment.
        state, info =   self._environment_.reset(seed = self._seed_)
            
        # Convert state to tensor.
        state:  Tensor =    tensor(state, dtype = float32, device = self._device_).unsqueeze(0)
        
        # Initialize reward tracking.
        episode_reward: float = 0.0
        
        # Until environment is solved...
        for step in count():
            
            # Select an action.
            action:     int =                               self.act(state = state)
            
            # Submit action.
            new_state, reward, terminal, truncated, meta =  self._environment_.step(action = action)
            
            # Track reward.
            episode_reward +=                               reward
            
            # Convert new state to tensor.
            new_state:  Tensor =                            tensor(
                                                                new_state,
                                                                dtype =     float32,
                                                                device =    self._device_
                                                            ).unsqueeze(0)
            
            # Observe transition.
            self.observe(state, action, reward, new_state, (terminal or truncated))
            
            # Episode concludes if new state is terminal/truncated.
            if terminal or truncated: break
            
            # Update current state.
            state =                                         new_state
            
        # Provide evaluation resutls.
        return {"reware": episode_reward, "steps": step}
        
    # HELPERS ======================================================================================
    
    def _decay_epsilon_(self) -> None:
        """# Decay Exploration Rate."""
        self._exploration_rate_:    float = max(
                                                self._exploration_min_,
                                                self._exploration_rate_ * self._exploration_decay_
                                            )
    
    def _explore_(self) -> int:
        """# Explore.
        
        ## Returns:
            * int:  Randomly sampled action from environment's action space.
        """
        # Debug action.
        self.__logger__.debug(f"Choosing to explore")
        
        # Sample environment's action space.
        return self._environment_.action_space.sample()
    
    def _get_q_values_(self,
        states:     Tensor,
        actions:    Tensor
    ) -> Tensor:
        """# Get Current Q-Values from Value Network.

        ## Args:
            * states    (Tensor):   States for which current Q-values are being provided.
            * actions   (Tensor):   Actions taken for corresponding states.

        ## Returns:
            * Tensor:   Q-values for states according to value network.
        """
        return self._value_(states).gather(1, actions.unsqueeze(1))
    
    @no_grad()
    def _get_target_q_values_(self,
        new_states: Tensor
    ) -> Tensor:
        """# Get Target Q-Values from Target Network.

        ## Args:
            * new_states    (Tensor):   States for which target Q-values are being provided.

        ## Returns:
            * Tensor:   Q-values for new states according to target network.
        """
        return self._target_(new_states).max(1)[0].unsqueeze(1)
    
    @no_grad()
    def _select_best_action_(self,
        state:  Tensor
    ) -> int:
        """# Select Best Action.
        
        ## Args:
            * state (Tensor):   State for which actino is being selected.
            
        ## Returns:
            * int:  Action selected for state.
        """
        # Debug action.
        self.__logger__.debug(f"Choosing best action for state = {state}")
        
        # Select best action via value network.
        return self._value_(state).argmax().item()
    
    def _train_value_network_(self) -> Optional[float]:
        """# Train Value Network on Experience.
        
        ## Returns:
            * float:    Loss calculation if training takes place.
        """
        # If replay buffer is not ready for sampling, defer training.
        if not self._memory_.is_ready_for_sampling: return None
        
        # Sample a batch of transitions from experience replay buffer.
        transitions:    List[Transition] =  self._memory_.sample().transitions
        
        # Convert batch to tensors
        states:             Tensor =            stack([t.state.squeeze() for t in transitions]).to(self._device_)
        actions:            Tensor =            LongTensor([t.action for t in transitions]).to(self._device_)
        rewards:            Tensor =            FloatTensor([t.reward for t in transitions]).to(self._device_)
        new_states:         Tensor =            stack([t.next_state.squeeze() for t in transitions]).to(self._device_)
        dones:              Tensor =            BoolTensor([t.done for t in transitions]).to(self._device_)
        
        # Get current Q-values.
        q_values:           Tensor =            self._get_q_values_(states = states, actions = actions)
        
        # Get target Q-values.
        target_q_values:    Tensor =            self._get_target_q_values_(new_states = new_states)
        
        # Discount target Q-values.
        target_q_values:    Tensor =            rewards.unsqueeze(1) + (self._discount_rate_ * target_q_values * (~dones).unsqueeze(1))
        
        # Compute loss.
        loss:               Tensor =            smooth_l1_loss(input = q_values, target = target_q_values)
        
        # Reset gradients.
        self._optimizer_.zero_grad()
        
        # Back propagation.
        loss.backward()
        
        # Clip gradients.
        clip_grad_value_(parameters = self._value_.parameters(), clip_value = 1.0)
        
        # Update weights.
        self._optimizer_.step()
        
        # Provide loss calculation.
        return loss.item()
    
    def _update_target_network_(self) -> None:
        """# Hard Update Target Network."""
        self._target_.load_state_dict(state_dict = self._value_.state_dict())