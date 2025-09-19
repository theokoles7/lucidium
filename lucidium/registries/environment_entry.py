"""# lucidium.registries.environment_entry

Defines the structure and utility of an environment registration entry.
"""

__all__ = ["EnvironmentEntry"]

from argparse           import _SubParsersAction
from logging            import Logger
from typing             import Callable, List, Optional

from gymnasium.spaces   import Space

from lucidium.utilities import get_child

class EnvironmentEntry():
    """# Environment Registry Entry
    
    Storage of environment registration entry data.
    """
    
    def __init__(self,
        name:               str,
        id:                 str,
        action_types:       List[Space],
        observation_types:  List[Space],
        tags:               Optional[List[str]],
        parser:             Callable
    ):
        """# Instantiate Environment Registration Entry.

        ## Args:
            * name              (str):                  Name of entry.
            * id                (str):                  ID used for `gymnasium.make()`.
            * action_types      (List[Space]):          Compatible action spaces.
            * observation_types (List[Space]):          Compatible observation spaces.
            * tags              (Optional[List[str]]):  Tags describing environment goals/tasks.
            * parser            (Callable):             Environment argument parser registration 
                                                        function.
        """
        # Initialize logger.
        self.__logger__:            Logger =                get_child(f"{name}-registration-entry")
        
        # Define properties.
        self._name_:                str =                   name
        self._id_:                  str =                   id
        self._action_types_:        List[Space] =           action_types
        self._observation_types_:   List[Space] =           observation_types
        self._tags_:                Optional[List[str]] =   tags
        self._parser_:              Callable =              parser
        
        # Debug initialization.
        self.__logger__.debug(f"Registered {name} entry ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @property
    def action_types(self) -> List[Space]:
        """# Environment Action Types."""
        return self._action_types_.copy()
    
    @property
    def id(self) -> str:
        """# Environment ID."""
    
    @property
    def name(self) -> str:
        """# Environment Name."""
        return self._name_
    
    @property
    def observation_types(self) -> List[Space]:
        """# Environment Observation Types."""
        return self._observation_types_.copy()
    
    @property
    def parser(self) -> Callable:
        """# Environment Parser Registration Function."""
        return self._parser_
    
    @property
    def tags(self) -> Optional[List[str]]:
        """# Environment Taxonomy Tags."""
        return self._tags_
    
    # METHODS ======================================================================================
    
    def contains_tag(self,
        tag:    str
    ) -> bool:
        """# Environment Contains Tag?

        ## Args:
            * tag   (str):  Tag being verified.

        ## Returns:
            * bool: True if environment contains tag.
        """
        # Log action for debugging.
        self.__logger__.debug(f"""{self._name_}-entry contains tag "{tag}": {tag in self._tags_}""")
        
        # Indicate that entry contains tag.
        return tag in self._tags_
    
    def register_parser(self,
        subparser: _SubParsersAction
    ) -> None:
        """# Register Parser.

        ## Args:
            * sub_parser    (_SubParsersAction):    Parent's sub parser.
        """
        # Log action for debugging.
        self.__logger__.debug(f"Registering {self._name_} parser under {subparser.dest}")
        
        # Register parser.
        self._parser_(subparser)
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation"""
        return f"""<{self._name_}({",".join(self._tags_)})>"""