"""# lucidium.registration.core.entry

Abstract registration entry implementation.
"""

from abc                                    import ABC
from argparse                               import _SubParsersAction
from logging                                import Logger
from typing                                 import Callable, List, Optional

from lucidium.registration.core.exceptions  import ParserNotConfiguredError
from lucidium.utilities                     import get_child

class Entry(ABC):
    """# Abstract Registration Entry"""
    
    def __init__(self,
        name:   str,
        tags:   List[str] =             [],
        parser: Optional[Callable] =    None
    ):
        """# Instantiate Entry.
        
        ## Args:
            * name      (str):              Name of entry.
            * tags      (List[str]):        Tags that describe the entry's taxonomy.
            * parser    (Callable | None):  Argument parser handler.
        """
        # Initialize logger.
        self.__logger__:    Logger =    get_child(f"{name}-registration-entry")
        
        # Define properties.
        self._name_:        str =                   name
        self._tags_:        List[str] =             tags
        self._parser_:      Optional[Callable] =    parser
        
        # Debug registration.
        self.__logger__.debug(f"Registered {name} entry")
        
    # PROPERTIES ===================================================================================
    
    @property
    def name(self) -> str:
        """# Entry Name."""
        return self._name_
    
    @property
    def parser(self) -> Optional[Callable]:
        """# Entry Argument Parser Handler."""
        return self._parser_
    
    @property
    def tags(self) -> List[str]:
        """# Entry Taxonomy Tags."""
        return self._tags_
    
    # METHODS ======================================================================================
    
    def contains_tag(self,
        tag:    str
    ) -> bool:
        """# Entry Contains Tag?

        ## Args:
            * tag   (str):  Tag being verified.

        ## Returns:
            * bool: True if entry contains tag.
        """
        # Debug verification.
        self.__logger__.debug(f"{self._name_.capitalize()} entry has tag {tag}? {tag in self._tags_}")
        
        # Indicate existence of tag.
        return tag in self._tags_
    
    def register_parser(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Entry Argument Parser.

        ## Args:
            * subparser (_SubParsersAction):    Parent's sub-parser.
            
        ## Raises:
            * ParserNotConfiguredError: If entry was not register with a parser handler.
        """
        # If entry was not registered with a parser handler, report error.
        if self._parser_ is None: raise ParserNotConfiguredError(entry_name = self._name_)
        
        # Debug action.
        self.__logger__.debug(f"Registering {self._name_} parser under {subparser.dest}")
        
        # Register parser.
        self._parser_(subparser)
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Entry Object Representation."""
        return f"""<{self._name_.capitalize()}Entry(tags = {",".join(self._tags_)})>"""