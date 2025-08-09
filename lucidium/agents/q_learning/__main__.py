"""# lucidium.agents.q_learning.main"""

from logging                    import Logger
from typing                     import Callable, Dict

from lucidium.agents.commands   import *
from lucidium.utilities         import get_child

def main(
    action: str,
    **kwargs
) -> None:
    """# Execute Q-Learning Action.

    ## Args:
        * action    (str):  Q-Learning action being executed.
    """
    # Initialize logger.
    _logger_:       Logger =            get_child(
                                            logger_name =   "q-learning.main"
                                        )
    
    # Define command mapping.
    _commands_:     Dict[str, Callable] =   {
                                                "play": play.main
    }
    
    try:# Execute action.
        _commands_[action](**kwargs)
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error caught in Q-Learning main process: {e}", exc_info = True)