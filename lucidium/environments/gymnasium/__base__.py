"""# lucidium.environments.gymnasium.base

Gymnasium environment wrapper.
"""

from typing                                     import Any, Dict, override

from gymnasium                                  import Env, make

from lucidium.environments.__base__             import Environment
from lucidium.environments.gymnasium.__args__   import register_gymnasium_parser
from lucidium.environments.gymnasium.__main__   import main
from lucidium.registration                      import register_environment

@register_environment(
    name =          "gymnasium",
    tags =          [],
    entry_point =   main,
    parser =        register_gymnasium_parser
)
class Gymnasium(Environment):
    """# Gymnasium Environment Wrapper.
    
    This wrapper class simply provides an interface for utilizing environments from Farama 
    Foundation's Gymnasium such that they adhere to Lucidium's environment specification.
    
    Based on: https://gymnasium.farama.org/
    """
    
    def __init__(self,
        id:                     str,
        max_episode_steps:      int =   None,
        disable_env_checker:    bool =  None,
        render_mode:            str =   None,
        **kwargs
    ):
        """# Gymnasium Environment Wrapper."""
        # Define properties.
        self._name_:    str =   id
        
        # Initialize environment.
        self._env_:     Env =   make(
                                    id =                    id,
                                    max_episode_steps =     max_episode_steps,
                                    disable_env_checker =   disable_env_checker,
                                    **kwargs
                                )
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def action_space(self) -> Any: return self._env_.action_space
    
    @override
    @property
    def name(self) -> str: return self._name_
    
    @override
    @property
    def observation_space(self) -> Any: return self._env_.observation_space
    
    @override
    @property
    def statistics(self) -> Dict[str, Any]: return self._env_.metadata
    
    # METHODS ======================================================================================
    
    @override
    def reset(self) -> Any: return self._env_.reset()
    
    @override
    def step(self, action: Any) -> Any: return self._env_.step(action = action)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str: return self._env_.__repr__()
    
    def __str__(self) -> str: return str(self._env_)