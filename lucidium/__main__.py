"""# lucidium.main

Lucidium application driver.
"""

from argparse               import Namespace
from logging                import Logger

from lucidium.__args__      import parse_lucidium_arguments
from lucidium.registries    import AGENT_REGISTRY, ENVIRONMENT_REGISTRY
from lucidium.utilities     import *

def main(*args, **kwargs) -> None:
    """# Execute Application."""
    # Parse arguments.
    _arguments_:    Namespace = parse_lucidium_arguments()
    
    # Initialize logger.
    _logger_:       Logger =    get_logger(
                                    logger_name =   "lucidium",
                                    logging_level = _arguments_.logging_level,
                                    logging_path =  _arguments_.logging_path
                                )
    
    try:# Log banner.
        _logger_.info(BANNER)
        
        # Dispatch agent commands.
        if _arguments_.command in AGENT_REGISTRY: AGENT_REGISTRY.dispatch(cls = _arguments_.command, *args, **kwargs)
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error: {e}", exc_info = True)
    
    # Exit gracefully.
    finally:                _logger_.debug("Exiting")

if __name__ == "__main__": main()