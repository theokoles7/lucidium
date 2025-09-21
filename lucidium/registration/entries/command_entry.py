"""# lucidium.registration.entries.command_entry

Defines the structure and utility of a command registry entry.
"""

__all__ = ["CommandEntry"]

from typing                             import Callable

from lucidium.registration.core.entry   import Entry

class CommandEntry(Entry):
    """# Command Entry
    
    Storage of command registration entry data.
    """
    
    def __init__(self,
        name:           str,
        entry_point:    Callable,
        parser:         Callable
    ):
        """# Instantiate Command Registration Entry.

        ## Args:
            * name          (str):      Name of command.
            * entry_point   (Callable): Command's main process entry point.
            * parser        (Callable): Command argument parser registeration handler.
        """
        # Initialize entry.
        super(CommandEntry, self).__init__(name = name, parser = parser)
        
        # Define properties.
        self._entry_point_: Callable =  entry_point
        
    # PROPERTIES ===================================================================================
    
    @property
    def entry_point(self) -> Callable:
        """# Command's Entry Point

        Command's main process entry point.
        """
        return self._entry_point_