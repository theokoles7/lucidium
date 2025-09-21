"""# lucidium.registration.entries.agent_entry

Defines the structure and utility of an agent registration entry.
"""

__all__ = ["AgentEntry"]

from typing                     import Callable, List, Optional, Type

from lucidium.registration.core import Entry

class AgentEntry(Entry):
    """# Agent Registry Entry
    
    Storage of class registration entry data.
    """
    
    def __init__(self,
        cls:            Type,
        name:           str,
        tags:           List[str] =             [],
        entry_point:    Optional[Callable] =    None,
        parser:         Callable =              None
    ):
        """# Instantiate Agent Registration Entry.

        ## Args:
            * cls           (Type):             Agent class being registered.
            * name          (str):              Name of entry.
            * tags          (List[str]):        Tags that describe the taxonomy of the agent being registered.
            * entry_point   (Callable | None):  Agent's entry point.
            * parser        (Callable):         Argument parser handler.
        """
        # Initialize entry.
        super(AgentEntry, self).__init__(name = name, tags = tags, parser = parser)
        
        # Define properties.
        self._cls_:         Type =      cls
        self._entry_point_: Callable =  entry_point
        
    # PROPERTIES ===================================================================================
    
    @property
    def cls(self) -> Type:
        """# Registered Class"""
        return self._cls_
    
    @property
    def entry_point(self) -> Callable:
        """# Classe's Entry Point."""
        return self._entry_point_