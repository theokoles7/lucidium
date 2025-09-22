"""# lucidium.agents.commands.train.main

Training process implementation & handling.
"""

from logging                                    import Logger
from typing                                     import Any, Dict, Literal

from gymnasium                                  import Env

from lucidium.agents.__base__                   import Agent
from lucidium.agents.commands.train.__args__    import register_train_parser
from lucidium.registration                      import AGENT_REGISTRY, ENVIRONMENT_REGISTRY, register_agent_command
from lucidium.utilities                         import get_child, TIMESTAMP

class TrainProcess():
    """# Agent Training Process.
    
    Process execution & handling for agent training.
    """
    
    def __init__(self,
        agent:                  str,
        environment:            str,
        episodes:               int =                                   1000,
        max_episode_steps:      int =                                   1000,
        evaluation_interval:    int =                                   100,
        render_mode:            Literal["human", "rgb_array", "ansi"] = None,
        save_model:             bool =                                  False,
        save_config:            bool =                                  False,
        save_results:           bool =                                  False,
        **kwargs
    ):
        """# Configure Training Process.

        ## Args:
            * agent                 (str):  Agent being trained.
            * environment           (str):  Environment on which agent will be trained.
            * episodes              (int):  Number of episodes for which training will be conducted. 
                                            Defaults to 1000.
            * max_episode_steps     (int):  Maximum number of steps allowed during each episode. 
                                            Defaults to 1000.
            * evaluation_interval   (int):  Interval at which agent will be evaluated. Defaults to 
                                            100.
            * render_mode           (str):  Mode by which environment will be rendered during 
                                            training. Default to None (will not be rendered). 
                                            **NOTE**: Contingent on environment specific rendering 
                                            capabilities.
            * save_model            (bool): Save model on conclusion of training process. Defaults
                                            to False.
            * save_config           (bool): Save agent & environment configurations on conclusion
                                            of training process. Defaults to False.
            * save_results          (bool): Save training statistics on conclusion of training 
                                            process. Defaults to False.
        """
        # Initialize logger.
        self.__logger__:            Logger =    get_child("training-process")
        
        # Define training parameters.
        self._episodes_:            int =       int(episodes)
        self._max_episode_steps_:   int =       int(max_episode_steps)
        self._evaluation_interval_: int =       int(evaluation_interval)
        self._save_model_:          bool =      bool(save_model)
        self._save_config_:         bool =      bool(save_config)
        
        # Initialize environment.
        self._environment_:         Env =       ENVIRONMENT_REGISTRY.load(
                                                    name =              environment,
                                                    max_episode_steps = max_episode_steps,
                                                    render_mode =       render_mode
                                                )
        
        # Initialize agent.
        self._agent_:               Agent =     AGENT_REGISTRY.load(
                                                    name =              agent,
                                                    environment =       self._environment_,
                                                    **kwargs
                                                )
        
        # Define patch for saving results.
        self._save_path_:           str =       f"output/train_{agent}_{environment}_{TIMESTAMP}"
        
        # Debug initialization.
        self.__logger__.debug(f"Initialized for {agent} training on {environment}")
        
    # METHODS ======================================================================================
    
    def execute(self) -> Dict[str, Any]:
        """# Execute Training Process.

        ## Returns:
            * Dict[str, Any]:   Training statistics/results.
        """
        # Initialize training statistics.
        statistics: Dict[str, Any] =    {
                                            "training":     {},
                                            "evaluation":   {},
                                            "MA10":         0,
                                            "MA50":         0,
                                            "MA100":        0
                                        }
        
        # For each episode prescribed...
        for episode in range(1, self._episodes_ + 1):
            
            # Train agent for one episode.
            statistics["training"][episode] =       self._agent_.train_episode()
            
            # If this is an evaluation interval...
            if episode % self._evaluation_interval_ == 0:
                
                # Evaluate agent for one episode.
                statistics["evaluation"][episode] = self._agent_.evaluate_episode()
                
                # Log evaluation.
                self.__logger__.info(f"""Episode {episode}/{self._episodes_}: {statistics["evaluation"][episode]}""")
                
        # Log training process completion.
        self.__logger__.info(f"Training completed.")
        
        # Save model if requested.
        if self._save_model_: self._agent_.save_model(path = self._save_path_)
        
@register_agent_command(
    name =      "train",
    parser =    register_train_parser
)
def agent_train_entry_point(**kwargs) -> Dict[str, Any]:
    """# Execute Agent-Training Process.
    
    ## Returns:
        * Dict[str, Any]:   Training statistics/results.
    """
    # Execute training process.
    return TrainProcess(**kwargs).execute()