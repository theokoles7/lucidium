"""# lucidium.agents.nlm.main"""

__all__ = ["main"]

from logging                import Logger

from lucidium.registries    import AGENT_COMMAND_REGISTRY
from lucidium.utilities     import get_child

def main(
    agent_action: str,
    **kwargs
) -> None:
    """# Execute NLM Action.

    ## Args:
        * agent_action  (str):  NLM action being executed.
    """
    # Initialize logger.
    _logger_:   Logger =    get_child(logger_name =   "nlm.main")
    
    try:# Log for debugging.
        _logger_.debug(f"Dispatching command {agent_action}")
        
        # Dispatch command.
        AGENT_COMMAND_REGISTRY.dispatch(command = agent_action, **{k:v for k, v in kwargs.items() if k != "command"})
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error caught in NLM main process: {e}", exc_info = True)