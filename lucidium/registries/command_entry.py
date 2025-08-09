"""# lucidium.registries.command_entry

Defines the structure and utility of a command registry entry.
"""

__all__ = ["CommandEntry"]

from argparse           import _SubParsersAction
from logging            import Logger
from typing             import Callable

from lucidium.utilities import get_child

class CommandEntry():
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
        # Initialize logger.
        self.__logger__:    Logger =    get_child(f"{name}-command-registration-entry")
        
        # Define properties.
        self._name_:        str =       name
        self._entry_point_: Callable =  entry_point
        self._parser_:      Callable =  parser
        
        # Log initialization for debugging.
        self.__logger__.debug(f"Registered {name} command entry ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @property
    def entry_point(self) -> Callable:
        """# Command's Entry Point

        Command's main process entry point.
        """
        return self._entry_point_
    
    @property
    def name(self) -> str:
        """# Command's Name"""
        return self._name_
    
    @property
    def parser(self) -> Callable:
        """# Command's Parser

        Command argument parser registeration handler.
        """
        return self._parser_
    
    # METHODS ======================================================================================
    
    def register_parser(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Parser.

        ## Args:
            * sub_parser    (_SubParsersAction):    Parent's sub parser.
        """
        # Log action for debugging.
        self.__logger__.debug(f"Registering {self._name_} command parser under {subparser.dest}")
        
        # Register parser.
        self._parser_(subparser)
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Command Entry Object Representation"""
        return f"""<CommandEntry(command = {self.name}, entry_point = {self.entry_point}, parser = {self.parser})>"""