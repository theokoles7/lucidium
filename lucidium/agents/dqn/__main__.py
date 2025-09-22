"""# lucidium.agents.dqn.main"""

__all__ = ["main"]

from logging                import Logger

from lucidium.registration  import AGENT_COMMAND_REGISTRY
from lucidium.utilities     import get_child

def dqn_entry_point(
    agent_action: str,
    **kwargs
) -> None:
    """# Execute DQN Action.

    ## Args:
        * agent_action  (str):  DQN action being executed.
    """
    # Initialize logger.
    _logger_:   Logger =    get_child(logger_name = "dqn.main")
    
    try:# Log for debugging.
        _logger_.debug(f"Dispatching command {agent_action}")
        
        # Dispatch command.
        AGENT_COMMAND_REGISTRY.dispatch(command = agent_action, **{k:v for k, v in kwargs.items() if k != "command"})
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error caught in DQN main process: {e}", exc_info = True)