"""# lucidium.registries.environment_registry

Defines the environment registry system.
"""

__all__ = ["EnvironmentRegistry"]

from argparse                               import _SubParsersAction
from logging                                import Logger
from typing                                 import Callable, Dict, List, Optional

from gymnasium.spaces                       import Space

from lucidium.registries.environment_entry  import EnvironmentEntry
from lucidium.utilities                     import get_child

class EnvironmentRegistry():
    """# Environment Registry
    
    Environment registry system with lazy loading.
    """
    
    def __init__(self,
        name:   str =   "environments"
    ):
        """# Instantiate Environment Registry.
        
        ## Args:
            * name  (str):  Name of the sub-module that the registry represents.
        """
        # Initialize logger.
        self.__logger__:    Logger =                        get_child(f"{name}-registry")
        
        # Define sub-module name.
        self._name_:        str =                           name
        
        # Initialize entry map.
        self._entries_:     Dict[str, EnvironmentEntry] =   {}
        
        # Initialize loaded flag.
        self._loaded_:      bool =                          False
        
    # PROPERTIES ===================================================================================
    
    @property
    def entries(self) -> Dict[str, EnvironmentEntry]:
        """# Environment Registry Entries"""
        return {name: entry.cls for name, entry in self._entries_.items()}.copy()
    
    @property
    def is_loaded(self) -> bool:
        """# Environment Registry is Loaded?"""
        return self._loaded_
    
    @property
    def name(self) -> str:
        """# Environment Registry Name."""
        return self._name_
    
    # METHODS ======================================================================================
    
    def get_entry(self,
        key:    str
    ) -> EnvironmentEntry:
        """# Get Environment Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * EnvironmentEntry: Environment registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # Log action for debugging.
        self.__logger__.debug(f"Getting entry: {key}")
        
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key]
    
    def list(self,
        filter_by:  Optional[List[str]] =   []
    ) -> Optional[List[str]]:
        """# List Entries.

        ## Args:
            * filter_by (List[str] | None): Tags by which entries will be filtered.

        ## Returns:
            * List[str] | None: List of entry names that satisfy tag filter(s).
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # Log action for debugging.
        self.__logger__.debug(f"Listing {self._name_} entries filtered by tags: {filter_by}")
        
        # If no filters are provided, simply return all entries.
        if not filter_by: return list(self._entries_.keys())
        
        # Otherwise, returned filtered entries.
        return  [
                    name for name, entry 
                    in self._entries_.items() 
                    if  all(
                            tag in entry.tags
                            for tag in filter_by
                        )
                ]
        
    def load_all(self) -> None:
        """# Load all Registered Modules."""
        # Simply return if registry has already been loaded.
        if self.is_loaded: return
        
        # Otherwise, import all modules...
        self._import_all_modules_()
        
        # Log action for debugging.
        self.__logger__.debug(f"{self._name_} registry is loaded")
        
        # Record that registry has now been loaded.
        self._loaded_:  bool =  True
        
    def register(self,
        name:               str,
        id:                 str,
        action_types:       List[Space],
        observation_types:  List[Space],
        tags:               Optional[List[str]],
        parser:             Callable
    ) -> None:
        """# Register Environment Entry.

        ## Args:
            * name              (str):                  Name of entry.
            * id                (str):                  ID used for `gymnasium.make()`.
            * action_types      (List[Space]):          Compatible action spaces.
            * observation_types (List[Space]):          Compatible observation spaces.
            * tags              (Optional[List[str]]):  Tags describing environment goals/tasks.
            * parser            (Callable):             Environment argument parser registration 
                                                        function.
        """
        # Assert that entry does not already exist.
        if name in self._entries_: raise ValueError(f"{name} is already registered.")
        
        # Debug registration parameters.
        self.__logger__.debug(f"Registering entry: name = {name}, id = {id}, actions = "\
            f"{action_types}, observations = {observation_types}, targs = {tags}, parser = {parser}")
        
        # Register entry.
        self._entries_[name] =  EnvironmentEntry(
                                    name =              name,
                                    id =                id,
                                    action_types =      action_types,
                                    observation_types = observation_types,
                                    tags =              tags,
                                    parser =            parser
                                )
        
    def register_parsers(self,
        parent_subparser:   _SubParsersAction
    ) -> None:
        """# Register Argument Parsers.

        ## Args:
            * parent_subparser  (_SubParsersAction):    Command sub parser of parent parser.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # For each registered item...
        for entry in self._entries_.values():
            
            # If entry contains argument parser...
            if entry.parser:
                
                # Log action for debugging.
                self.__logger__.debug(f"Registering parser for {entry.name}")
                
                # Register parser.
                entry.register_parser(subparser = parent_subparser)
        
    # HELPERS ======================================================================================
    
    def _ensure_loaded_(self) -> None:
        """# Ensure Agent Registry is Loaded."""
        if not self.is_loaded: self.load_all()
        
    def _import_all_modules_(self) -> None:
        """# Import All Modules.
        
        Dynamically import all modules in the package to trigger decorators.
        """
        from importlib  import import_module
        from pkgutil    import walk_packages
        from types      import ModuleType
        
        # Import the main package to get its path.
        package:    ModuleType = import_module(f"lucidium.{self._name_}")
        
        # Log for debugging.
        self.__logger__.debug(f"Walking {package}")
        
        try:# Walk through all modules in the package.
            for _, module, _ in walk_packages(
                path =      package.__path__,
                prefix =    f"lucidium.{self._name_}.",
                onerror =   lambda x: None
            ):
                try:# Attempt import of module.
                    import_module(name = module)
                    
                    # Log for debugging.
                    self.__logger__.debug(f"Walked {module}")
                    
                # If a module cannot be imported...
                except ImportError as e:
                    
                    # Report error.
                    print(f"Error importing {module} module: {e}")
                   
        # If a package cannot be imported...
        except ImportError as e:
                    
            # Report error.
            print(f"Error importing {package} package: {e}")
        
    # DUNDERS ======================================================================================
    
    def __contains__(self,
        key:    str
    ) -> bool:
        """# ClassRegistry Contains Key?
        
        True if key is registered.
        """
        return key in self._entries_
    
    def __getitem__(self,
        key:    str
    ) -> EnvironmentEntry:
        """# Get Environment Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * EnvironmentEntry: Environment Registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key].cls
    
    def __len__(self) -> int:
        """# Number of Registrations."""
        return len(self._entries_)
    
    def __repr__(self) -> str:
        """# Agent Registry Object Representation"""
        return f"""<EnvironmentRegistry({len(self._entries_)} entries)>"""