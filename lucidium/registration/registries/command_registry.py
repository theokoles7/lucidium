"""# lucidium.registration.registries.command_registry

Defines the command registry system.
"""

__all__ = ["CommandRegistry"]

from typing                         import Any, Dict, override

from lucidium.registration.core     import Registry, EntryPointNotConfiguredError
from lucidium.registration.entries  import CommandEntry

class CommandRegistry(Registry):
    """# Command Registry
    
    Command registry system.
    """
    
    def __init__(self,
        name:   str
    ):
        """# Instantiate Command Registry.

        ## Args:
            * name  (str):  Name of the class that the registry stores commands for.
        """
        # Initialize registry.
        super(CommandRegistry, self).__init__(name = name)
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def entries(self) -> Dict[str, CommandEntry]:
        """# Command Registry Entries"""
        return self._entries_
    
    # METHODS ======================================================================================
    
    def dispatch(self,
        command:    str,
        **kwargs
    ) -> Any:
        """# Dispatch (Command).

        ## Args:
            * command   (str):  Command to which arguments are being dispatched.

        ## Returns:
            * Any:  Data returned from command.
        """
        # Get the command entry.
        entry:  CommandEntry =  self.get_entry(key = command)
        
        # Log action for debugging.
        self.__logger__.debug(f"Dispatching to {command} with arguments: {kwargs}")
        
        # Dispatch command.
        return entry.entry_point(**kwargs)
        
    # HELPERS ======================================================================================
    
    @override
    def _create_entry_(self, **kwargs) -> CommandEntry:
        """# Create Command Entry.

        ## Returns:
            * CommandEntry: New command entry instance.
        """
        return CommandEntry(**kwargs)
            
    # DUNDERS ======================================================================================
    
    @override
    def __getitem__(self,
        key:    str
    ) -> CommandEntry:
        """# Get Command Entry.

        ## Args:
            * key (str):    Name of command entry being fetched.

        ## Returns:
            * CommandEntry: Agent entry requested.
        """
        return self.get_entry(key = key)