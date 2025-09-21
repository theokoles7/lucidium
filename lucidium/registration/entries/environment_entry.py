"""# lucidium.registration.entries.environment_entry

Defines the structure and utility of an environment registration entry.
"""

__all__ = ["EnvironmentEntry"]

from typing                             import Callable, List

from gymnasium.spaces                   import Space

from lucidium.registration.core.entry   import Entry

class EnvironmentEntry(Entry):
    """# Environment Registry Entry
    
    Storage of environment registration entry data.
    """
    
    def __init__(self,
        name:               str,
        id:                 str,
        action_types:       List[Space],
        observation_types:  List[Space],
        parser:             Callable,
        tags:               List[str] =     []
    ):
        """# Instantiate Environment Registration Entry.

        ## Args:
            * name              (str):          Name of entry.
            * id                (str):          ID used for `gymnasium.make()`.
            * action_types      (List[Space]):  Compatible action spaces.
            * observation_types (List[Space]):  Compatible observation spaces.
            * tags              (List[str]):    Tags describing environment goals/tasks.
            * parser            (Callable):     Environment argument parser registration 
                                                        function.
        """
        # Initialize entry.
        super(EnvironmentEntry, self).__init__(name = name, tags = tags, parser = parser)
        
        # Define properties.
        self._id_:                  str =           id
        self._action_types_:        List[Space] =   action_types
        self._observation_types_:   List[Space] =   observation_types
        
    # PROPERTIES ===================================================================================
    
    @property
    def action_types(self) -> List[Space]:
        """# Environment Action Types."""
        return self._action_types_.copy()
    
    @property
    def id(self) -> str:
        """# Environment ID."""
        return self._id_
    
    @property
    def observation_types(self) -> List[Space]:
        """# Environment Observation Types."""
        return self._observation_types_.copy()