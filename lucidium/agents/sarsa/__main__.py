"""# lucidium.agents.sarsa.main"""

from logging                import Logger

from lucidium.registration  import AGENT_COMMAND_REGISTRY
from lucidium.utilities     import get_child

def main(
    agent_action: str,
    **kwargs
) -> None:
    """# Execute SARSA Action.

    ## Args:
        * agent_action  (str):  SARSA action being executed.
    """
    # Initialize logger.
    _logger_:       Logger =            get_child(
                                            logger_name =   "sarsa.main"
                                        )
    
    try:# Log for debugging.
        _logger_.debug(f"Dispatching action: {agent_action}")
        
        # Dispatch command.
        AGENT_COMMAND_REGISTRY.dispatch(command = agent_action, **{k:v for k, v in kwargs.items() if k != "command"})
    
    except Exception as e:  _logger_.critical(f"Unexpected error caught in SARSA main process: {e}", exc_info = True)