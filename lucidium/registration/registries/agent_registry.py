"""# lucidium.registration.registries.agent_registry

Defines the agent registry system.
"""

__all__ = ["AgentRegistry"]

from typing                         import Any, Dict, override, Type

from lucidium.registration.core     import Registry, EntryPointNotConfiguredError
from lucidium.registration.entries  import AgentEntry

class AgentRegistry(Registry):
    """# Agent Registry
    
    Agent registry system with lazy loading.
    """
    
    def __init__(self,
        name:   str =   "agents"
    ):
        """# Instantiate Agent Registry.
        
        ## Args:
            * name  (str):  Name of the sub-module that the registry represents.
        """
        # Initialize registry.
        super(AgentRegistry, self).__init__(name = name)
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def entries(self) -> Dict[str, AgentEntry]:
        """# Registry Entries."""
        return self._entries_.copy()
        
    # METHODS ======================================================================================
    
    def dispatch(self,
        name:   str,
        *args,
        **kwargs
    ) -> Any:
        """# Dispatch Command.

        ## Args:
            * name  (str):  Name of agent to whom arguments will be dispatched.
            
        ## Raises:
            * EntryPointNotConfiguredError: If entry was not registered with an entry point.

        ## Returns:
            * Any:  Data returned from command.
        """
        # Fetch entry according to name.
        entry:  AgentEntry =    self.get_entry(key = name)
        
        # If entry was not registered with an entry point...
        if entry.entry_point is None:
            
            # Report error.
            raise EntryPointNotConfiguredError(entry_name = name)
        
        # Log action for debugging.
        self.__logger__.debug(f"Dispatching to {name} with arguments: {kwargs}")
        
        # Dispatch to classe's entry point.
        return entry.entry_point(*args, **kwargs)
        
    def load(self,
        name:       str,
        **kwargs
    ) -> Any:
        """# Load Registered Class.

        ## Args:
            * name  (str):  Agent Registry entry name.

        ## Returns:
            * Agent:    Instantiated agent.
        """
        # Fetch entry according to name.
        entry:  AgentEntry =    self.get_entry(key = name)
        
        # Extract class.
        cls:    Type =          entry.cls
        
        # Log action for debugging.
        self.__logger__.debug(f"Loading {name} with arguments: {kwargs}")
        
        # Load class.
        return cls(**kwargs)
        
    # HELPERS ======================================================================================
    
    @override
    def _create_entry_(self, **kwargs) -> AgentEntry:
        """# Create Agent Entry.

        ## Returns:
            * AgentEntry:   New agent entry instance.
        """
        return AgentEntry(**kwargs)
            
    # DUNDERS ======================================================================================
    
    @override
    def __getitem__(self,
        key:    str
    ) -> AgentEntry:
        """# Get Agent Entry.

        ## Args:
            * key (str):    Name of agent entry being fetched.

        ## Returns:
            * AgentEntry:   Agent entry requested.
        """
        return self.get_entry(key = key)