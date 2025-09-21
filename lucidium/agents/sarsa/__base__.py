"""# lucidium.agents.sarsa.base

Implementation based on "Online SARSA Using Connectionist Systems" by Rummery & Niranjan 
(1994).
Link to paper: https://www.researchgate.net/profile/Mahesan-Niranjan/publication/2500611_On-Line_SARSA_Using_Connectionist_Systems/links/5438d5db0cf204cab1d6db0f/On-Line-SARSA-Using-Connectionist-Systems.pdf?_sg%5B0%5D=HYd0h230b7WOR6m4hj5yx01K97aS61Z0DufUURMQr9ZqMqcEVZ0dNpG84h6uCfRl_M40FNkXgRX-GnpnxH31Ww.jBF3fgrlhaJYs3bDEaHQU22nRpKP0zKeF_oOsqh7WddL8pfxAomPSbeANzdmLP9YPB26HbLeSaEJqhFgzIxvWQ&_sg%5B1%5D=CZtZhHTEMgSwBZrpZU_7BACd8RH04JUKiITdXRQJ6MQ9SFS27jreZmcsuNcqYYWRoxcwBE-xBMbrfl1QobmEZ65bmkmpzonq5JoLRIIUKXne.jBF3fgrlhaJYs3bDEaHQU22nRpKP0zKeF_oOsqh7WddL8pfxAomPSbeANzdmLP9YPB26HbLeSaEJqhFgzIxvWQ&_iepl=
"""

from logging                            import Logger
from typing                             import Any, Dict, Literal, override, Optional

from gymnasium.spaces                   import Space
from numpy.random                       import rand

from lucidium.agents.__base__           import Agent
from lucidium.agents.sarsa.__args__     import register_sarsa_parser
from lucidium.agents.sarsa.__main__     import main
from lucidium.registration              import register_agent
from lucidium.tabular                   import QTable
from lucidium.utilities                 import get_child

@register_agent(
    name =          "sarsa",
    tags =          ["on-policy", "tabular-based", "value-based", "temporal-difference"],
    entry_point =   main,
    parser =        register_sarsa_parser
)
class SARSA(Agent):
    """# SARSA Agent
    
    SARSA (State-Action-Reward-State-Action) is an on-policy temporal difference control algorithm. 
    Unlike SARSA, SARSA updates Q-values using the actual next action that will be taken 
    according to the current policy, making it an on-policy method.
    
    Implementation based on "Online SARSA Using Connectionist Systems" by Rummery & Niranjan 
    (1994).
    Link to paper: https://www.researchgate.net/profile/Mahesan-Niranjan/publication/2500611_On-Line_SARSA_Using_Connectionist_Systems/links/5438d5db0cf204cab1d6db0f/On-Line-SARSA-Using-Connectionist-Systems.pdf?_sg%5B0%5D=HYd0h230b7WOR6m4hj5yx01K97aS61Z0DufUURMQr9ZqMqcEVZ0dNpG84h6uCfRl_M40FNkXgRX-GnpnxH31Ww.jBF3fgrlhaJYs3bDEaHQU22nRpKP0zKeF_oOsqh7WddL8pfxAomPSbeANzdmLP9YPB26HbLeSaEJqhFgzIxvWQ&_sg%5B1%5D=CZtZhHTEMgSwBZrpZU_7BACd8RH04JUKiITdXRQJ6MQ9SFS27jreZmcsuNcqYYWRoxcwBE-xBMbrfl1QobmEZ65bmkmpzonq5JoLRIIUKXne.jBF3fgrlhaJYs3bDEaHQU22nRpKP0zKeF_oOsqh7WddL8pfxAomPSbeANzdmLP9YPB26HbLeSaEJqhFgzIxvWQ&_iepl=
    """
    
    def __init__(self,
        action_space:           Space,
        observation_space:      Space,
        learning_rate:          float =                                                     0.1,
        discount_rate:          float =                                                     0.99,
        exploration_rate:       float =                                                     1.0,
        exploration_decay:      float =                                                     0.99,
        exploration_min:        float =                                                     0.01,
        decay_interval:         Literal["by-step", "by-episode"] =                          "by-step",
        initialization_method:  Literal["zeros", "random", "small-random", "optimistic"] =  "zeros",
        **kwargs
    ):
        """# Instantiate SARSA Agent.
    
        The SARSA update rule is:
        
        Q(S,A) ← Q(S,A) + α[R + γQ(S',A') - Q(S,A)]
        
        Where A' is the action actually selected in state S' according to the current ε-greedy 
        policy.

        ## Args:
            * action_space          (Space):    Number of possible actions that the agent can take.
            * observation_space     (Space):    Dimensions of the environment in which the agent 
                                                will act.
            * learning_rate         (float):    Controls how much new information overrides old 
                                                information when updating Q-values. A higher 
                                                learning rate means the agent learns faster, 
                                                updating Q-values more significantly with new 
                                                experiences. Conversely, a lower learning rate leads 
                                                to more gradual updates, potentially stabilizing 
                                                training but slowing down convergence. Defaults to 
                                                0.1.
            * discount_rate         (float):    Determines the importance of future rewards. A 
                                                factor of 0 will make the agent "myopic" (or 
                                                short-sighted) by only considering current rewards, 
                                                while a factor approaching 1 will make it strive for 
                                                a long-term high reward. Defaults to 0.99.
            * exploration_rate      (float):    Probability that the agent will choose a random 
                                                action, rather than selecting the action that is 
                                                believed to be optimal based on its current 
                                                knowledge (i.e., the action with the highest 
                                                Q-value). When set high, the agent is more likely 
                                                to explore new actions. When low, the agent favors 
                                                exploiting its current knowledge. Defaults to 1.0.
            * exploration_decay     (float):    Controls how quickly the exploration rate decreases 
                                                over time. The exploration rate determines how often 
                                                the agent selects random actions (explores) versus 
                                                exploiting its learned knowledge (selecting the best 
                                                action based on Q-values). A decay factor less than 
                                                1 (e.g., 0.995) causes the exploration rate to 
                                                gradually decrease, leading to more exploitation as 
                                                the agent learns more about the environment. 
                                                Defaults to 0.99.
            * exploration_min       (float):    Specifies the minimum exploration rate that the gent 
                                                will reach after the exploration decay process. This 
                                                ensures that the agent does not completely stop 
                                                exploring and retains a small chance to explore 
                                                randomly, even in later stages of training. By 
                                                setting a minimum value for exploration, the agent 
                                                can still occasionally discover new actions, 
                                                avoiding getting stuck in a local optimum. Defaults 
                                                to 0.01.
            * decay_interval        (str):      Interval by which exploration rate (epsilon) will 
                                                decay. Defaults to "by-step".
                * by-step:      Decaying every step by a small rate is conventional.
                * by-episode:   Decaying by episode by a larger rate is unconventional.
            * initialization_method (str):      Initialize Q-Table with specific values (defaults to 
                                                "zeros"):
                * zeros:        Common choice when you assume that the agent has no prior knowledge 
                                of the environment and should learn everything from scratch. All 
                                states and actions start with equal value.
                * random:       Useful when you want the agent to start with some variability in its 
                                Q-values and potentially avoid any symmetry in the learning process. 
                                It may help in environments where different actions in the same 
                                state can have varying levels of importance or expected rewards.
                * small-random: Similar to random initialization, but with smaller values to prevent 
                                large, unrealistic initial biases. It's a good choice when you want 
                                to start with some exploration but without the extreme variance that 
                                might come with large random values.
                * optimistic:   Used to encourage exploration by making every state-action pair 
                                initially appear to be rewarding. Over time, the agent will update 
                                these values based on the actual rewards received.
        """
        # Initialize logger.
        self.__logger__:    Logger =    get_child("sarsa")
        
        # Define environment components.
        self._action_space_:        Space =         action_space
        self._observation_space_:   Space =         observation_space
        
        # Define learning parameters.
        self._learning_rate_:       float =         learning_rate
        
        # Define discount parameters.
        self._discount_rate_:       float =         discount_rate
        
        # Define exploration parameters.
        self._exploration_rate_:    float =         exploration_rate
        self._exploration_decay_:   float =         exploration_decay
        self._exploration_min_:     float =         exploration_min
        self._decay_interval_:      str =           decay_interval
        
        # Initialize Q-Table.
        self._q_table_:             QTable =        QTable(
                                                        action_space =          self._action_space_,
                                                        initialization_method = initialization_method
                                                    )
        
        # Track current state and action for SARSA update.
        self._next_state_:          int =           None
        self._next_action_:         int =           None
        
        # Log for debugging.
        self.__logger__.debug(f"Initialized SARSA agent {locals()}")
        
    # PROPERTIES ===================================================================================
    
    @property
    def alpha(self) -> float:
        """# Learning Rate (float)

        Controls how much new information overrides old information when updating Q-values.
        """
        return self._learning_rate_
    
    @property
    def current_action(self) -> int:
        """# Current Action
        
        The action currently being executed (needed for SARSA updates).
        """
        return self._current_action_
    
    @property
    def current_state(self) -> int:
        """# Current State
        
        The state the agent is currently in (needed for SARSA updates).
        """
        return self._current_state_
    
    @property
    def discount_rate(self) -> float:
        """# Discount Rate (float)

        Determines the importance of future rewards.
        """
        return self._discount_rate_
    
    @property
    def epsilon(self) -> float:
        """# Exploration Rate (float)

        Probability that the agent will choose a random action, rather than selecting the action 
        that is believed to be optimal based on its current knowledge (i.e., the action with the 
        highest Q-value).
        """
        return self._exploration_rate_
    
    @property
    def exploration_decay(self) -> float:
        """# Exploration Decay (float)

       Controls how quickly the exploration rate decreases over time. The exploration rate 
       determines how often the agent selects random actions (explores) versus exploiting its 
       learned knowledge (selecting the best action based on Q-values).
        """
        return self._exploration_decay_
    
    @property
    def exploration_min(self) -> float:
        """# Exploration Minimum (float)

        Specifies the minimum exploration rate that the agent will reach after the exploration decay 
        process.
        """
        return self._exploration_min_
    
    @property
    def exploration_rate(self) -> float:
        """# Exploration Rate (float)
        
        Probability that the agent will choose a random action, rather than selecting the action 
        that is believed to be optimal based on its current knowledge (i.e., the action with the 
        highest Q-value).
        """
        return self._exploration_rate_
    
    @property
    def gamma(self) -> float:
        """# Discount Rate (float)

        Determines the importance of future rewards.
        """
        return self._discount_rate_
    
    @property
    def learning_rate(self) -> float:
        """# Learning Rate (float)

        Controls how much new information overrides old information when updating Q-values.
        """
        return self._learning_rate_
    
    @override
    @property
    def name(self) -> str:
        """# (SARSA) Name

        SARSA agent' proper name.
        """
        return "SARSA"
    
    @override
    @property
    def statistics(self) -> Dict[str, Any]:
        """# (SARSA) Statistics

        Statistics pertaining to SARSA performance/status.
        """
        return  {
                    "learning_rate":        self._learning_rate_,
                    "discount_rate":        self._discount_rate_,
                    "eploration_rate":      self._exploration_rate_,
                    "exploration_decay":    self._exploration_decay_,
                    "exploration_min":      self._exploration_min_,
                    "decay_interval":       self._decay_interval_
                }
    
    # SETTERS ======================================================================================
    
    @epsilon.setter
    def epsilon(self,
        value:  float
    ) -> None:
        """# Set Exploration Rate.
        
        Value will be set as the maximum between the value provided and the minimum exploration rate 
        defined at agent initialization.

        ## Args:
            * value (float):    New exploration rate value.

        ## Raises:
            * AssertionError:   If value is not a float.
        """
        # Assert that value is a float.
        assert isinstance(value, float), f"Value expected to be float, got {type(value)}"
        
        # Set new exploration rate.
        self._exploration_rate_:    float = max(value, self.exploration_min)
        
    @exploration_rate.setter
    def exploration_rate(self,
        value:  float
    ) -> None:
        """# Set Exploration Rate.
        
        Value will be set as the maximum between the value provided and the minimum exploration rate 
        defined at agent initialization.

        ## Args:
            * value (float):    New exploration rate value.

        ## Raises:
            * AssertionError:   If value is not a float.
        """
        # Assert that value is a float.
        assert isinstance(value, float), f"Value expected to be float, got {type(value)}"
        
        # Set new exploration rate.
        self._exploration_rate_:    float = max(value, self.exploration_min)
    
    # METHODS ======================================================================================
    
    @override
    def act(self,
        state:  int
    ) -> int:
        """# Select Action.
        
        Choose an action using epsilon-greedy policy.

        ## Args:
            * state (int):  Current state of agent.

        ## Returns:
            * int:  Index of action chosen.
        """
        # If agent is beginning a new episode...
        if getattr(self, "_current_state_", None) is None:
            
            # Define initial state and action.
            self._current_action_:  int =   self._choose_action_(state = state)
            self._current_state_:   int =   state
            
        # Provide chosen action.
        return self._current_action_
    
    def decay_epsilon(self) -> None:
        """# Decay Exploration Rate.
        
        Update exploration rate to be the maximum between the current rate decayed or the defined 
        minimum exploration rate value.
        """
        # Administer exploration rate decay.
        self.exploration_rate *= self.exploration_decay
        
        # Log action for debugging.
        self.__logger__.debug(f"Exploration rate updated to {self._exploration_rate_}")
    
    @override
    def load_model(self,
        path:   str
    ) -> None:
        """# Load Model.
        
        Load agent's Q-table from file.

        ## Args:
            * path  (str):  Path at which model can be located/loaded.
        """
        # Log action for debugging.
        self.__logger__.debug(f"Loading q-table from {path}")
        
        # Save Q-table to file.
        self._q_table_.load(path = path)
    
    from typing import Any, Dict, Optional

    @override
    def observe(self,
        new_state:  int,
        reward:     float,
        done:       bool
    ) -> Optional[Dict[str, Any]]:
        """# Observe.
        
        Update Q(S,A) using SARSA update:
        
        Q(S,A) ← Q(S,A) + α · δ
        
        Where:
            * δ (TD error) = target − Q(S,A)
            * target = R + γ · Q(S', A')     (or target = R if terminal)
            * A' is the *policy's* next action (on-policy)

        ## Args:
            * new_state (Any):      State of environment after action was submitted.
            * reward    (float):    Reward yielded/penalty incurred by action submitted to 
                                    environment.
            * done      (bool):     Flag indicating if new state is terminal.
        
        ## Returns:
            * Dict[str, float] | None: Agent observation metrics.
        """
        # If we don't have a current (S, A), we can't update yet (e.g., very first call).
        if self._current_state_ is None or self._current_action_ is None: return

        # 1. What was our current estimate? Q(S, A)
        q_old:              float =         self._q_table_[self._current_state_][self._current_action_]

        # 2) Choose next action A' according to the *current policy* (on-policy), unless this is a terminal transition.
        A_next:             Optional[int] = None if done else self._choose_action_(state = new_state)
        best_next_value:    float =         0.0 if done else self._q_table_[new_state][A_next]

        # 3) Bootstrapped target for SARSA: R + γ * Q(S', A')  (or just R if terminal).
        target:             float =         reward + (self._discount_rate_ * best_next_value)

        # 4) TD (Temporal-Difference) error.
        td_error:           float =         target - q_old

        # 5) Update rule: move Q(S,A) toward the target by a fraction α (learning rate).
        q_new:              float =         q_old + self._learning_rate_ * td_error
        
        # Update Q-Table.
        self._q_table_[self._current_state_][self._current_action_] = q_new

        # Debug logging with decomposed terms
        self.__logger__.debug(
            f"""SARSA update | S={self._current_state_}, A={self._current_action_}, """
            f"""R={reward}, S'={new_state}, A'={A_next}, done={done} | """
            f"""q_old={q_old:.6f}, target={target:.6f}, td_error={td_error:.6f}, q_new={q_new:.6f}"""
        )

        # Advance the on-policy buffer for the next step.
        self._current_state_ =  None if done else new_state
        self._current_action_ = None if done else A_next
        self._next_action_ =    None

        # Decay exploration rate (epsilon).
        if done or self._decay_interval_ == "by-step": self.decay_epsilon()

        # Return observation.
        return  {
                    "q_old":    q_old,
                    "target":   target,
                    "td_error": td_error,
                    "q_new":    q_new
                }
        
    def save_config(self,
        path:   str
    ) -> None:
        """# Save Model Configuration.

        ## Args:
            * path  (str):  Path at which agent confriguration file will be saved.
        """
        from json   import dump
        from os     import makedirs
        
        # Ensure that path exists.
        makedirs(name = path, exist_ok = True)
        
        # Save configuratino to JSON file.
        dump(
            obj =       {
                            "learning_rate":        self._learning_rate_,
                            "discount_rate":        self._discount_rate_,
                            "exploration_rate":     self._exploration_rate_,
                            "exploration_decay":    self._exploration_decay_,
                            "exploration_min":      self._exploration_min_,
                            "bootstrap":            self._bootstrap_
                        },
            fp =        open(f"{path}/sarsa_config.json", "w"),
            indent =    2,
            default =   str
        )
        
        # Log save location.
        self.__logger__.info(f"SARSA configuration saved to {path}/sarsa_config.json")
    
    @override
    def save_model(self,
        path:   str
    ) -> None:
        """# Save Model
        
        Save agent's Q-table to file.

        ## Args:
            * path  (str):  Path at which model will be saved.
        """
        # Log action for debugging.
        self.__logger__.debug(f"Saving q-table to {path}")
        
        # Save Q-table to file.
        self._q_table_.save(path = path)
        
    # HELPERS ======================================================================================
    
    def _choose_action_(self,
        state:  int
    ) -> int:
        """# Choose Action.
        
        Choose action based on state provided, using an epsilon-greedy policy.

        ## Args:
            * state (int):  State for which an action needs to be chosen.

        ## Returns:
            * int:  Chosen action.
        """
        return  (
                    self._action_space_.sample()        \
                    if rand() < self._exploration_rate_ \
                    else self._q_table_.get_best_action(state = state)
                )