"""# lucidium.environments.grid_world.main

Grid World environment main process entry point.
"""

__all__ = ["main"]

from logging                import Logger

from lucidium.registries    import ENVIRONMENT_COMMAND_REGISTRY
from lucidium.utilities     import get_child

def main(
    action: str,
    **kwargs
) -> None:
    # Initialize logger.
    _logger_:   Logger =    get_child(logger_name = "grid-world.main")
    
    try:# Log for debugging.
        _logger_.debug(f"Dispatching command {action}")
        
        # Dispatch command.
        ENVIRONMENT_COMMAND_REGISTRY.dispatch(command = action, **{k:v for k, v in kwargs.items() if k != "command"})
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error caught in Grid World main process: {e}", exc_info = True)