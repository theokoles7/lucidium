"""# lucidium.registries.entry

Defines the structure and utility of a registration entry.
"""

from argparse   import _SubParsersAction
from typing     import Callable, List, Optional, Type

class RegistryEntry():
    """# Registry Entry
    
    Storage of registration entry data.
    """
    
    def __init__(self,
        cls:    Type,
        name:   str,
        tags:   Optional[List[str]] =   [],
        parser: Optional[Callable] =    None
    ):
        """# Instantiate Registration Entry

        ## Args:
            * cls       (Type):                 Class being registered.
            * name      (str):                  Name of entry.
            * tags      (Optional[List[str]]):  Tags that describe the taxonomy of the class being registered.
            * parser    (Optional[Callable]):   Argument parser handler.
        """
        # Define properties.
        self._cls_:     Type =      cls
        self._name_:    str =       name
        self._tags_:    List[str] = tags
        self._parser_:  Callable =  parser
        
    # PROPERTIES ===================================================================================
    
    @property
    def cls(self) -> Type:
        """# Registered Class"""
        return self._cls_
    
    @property
    def tags(self) -> Optional[List[str]]:
        """# Entry Tags."""
        return self._tags_
        
    # METHODS ======================================================================================
    
    def contains_tag(self,
        tag:    str
    ) -> bool:
        """# (Entry) Contains Tag?

        ## Args:
            * tag   (str):  Tag being verified.

        ## Returns:
            * bool: True if entry contains tag.
        """
        return tag in self._tags_
    
    def register_parser(self,
        subparser: _SubParsersAction
    ) -> None:
        """# Register Parser.

        ## Args:
            * sub_parser    (_SubParsersAction):    Parent's sub parser.
        """
        self._parser_(sub_parser)
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation"""
        return f"""<{self._name_}({",".join(self._tags_)})>"""