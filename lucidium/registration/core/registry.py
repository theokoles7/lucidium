"""# lucidium.registration.core.registry

Abstract registry implementation.
"""

from abc                                    import ABC, abstractmethod
from argparse                               import _SubParsersAction
from logging                                import Logger
from typing                                 import Dict, List

from lucidium.registration.core.entry       import Entry
from lucidium.registration.core.exceptions  import DuplicateEntryError, EntryNotFoundError
from lucidium.registration.core.types       import EntryType
from lucidium.utilities                     import get_child

class Registry(ABC):
    """# Abstract Registry"""
    
    def __init__(self,
        name:   str
    ):
        """# Instantiate Registry.

        ## Args:
            * name  (str):  Registry name.
        """
        # Initialize logger.
        self.__logger__:    Logger =            get_child(f"{name}-registry")
        
        # Define name.
        self._name_:        str =               name
        
        # Initialize entries map.
        self._entries_:     Dict[str, Entry] =  {}
        
        # Initialize flag indicating registry status.
        self._loaded_:      bool =              False
        
    # PROPERTIES ===================================================================================
    
    @property
    def entries(self) -> Dict[str, Entry]:
        """# Registry Entries."""
        return self._entries_.copy()
    
    @property
    def is_loaded(self) -> bool:
        """# Registry has been Loaded?"""
        return self._loaded_
    
    @property
    def name(self) -> str:
        """# Registry Name."""
        return self._name_
    
    # METHODS ======================================================================================
    
    def get_entry(self,
        key:    str
    ) -> Entry:
        """# Get Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.
            
        ## Raises:
            * EntryNotFoundError:   If entry is not registered.

        ## Returns:
            * Entry:    Entry requested.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # If key is not registered...
        if key not in self._entries_:
            
            # Report error.
            raise EntryNotFoundError(entry_name = key, registry_name = self._name_)
        
        # Debug action.
        self.__logger__.debug(f"Getting entry: {key}")
        
        # Provide requested entry.
        return self._entries_[key]
    
    def list(self,
        filter_by:  List[str] = []
    ) -> List[str]:
        """# List Entries.

        ## Args:
            * filter_by (List[str]):    Tags by which to filter entries.

        ## Returns:
            * List[str]:    List of [filtered] entries.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # Debug action.
        self.__logger__.debug(f"Listing {self._name_} entries filter by {filter_by}")
        
        # If no filter is provided, return all entries.
        if len(filter_by) == 0: return list(self._entries_.keys())
        
        # Otherwise, return filtered entries.
        return  [
                    name 
                    for name, entry
                    in self._entries_.items()
                    if  all(
                            tag in entry.tags
                            for tag
                            in filter_by
                        )
                ]
        
    def load_all(self) -> None:
        """# Load All Registered Modules."""
        # If registry is already loaded, no-op.
        if self.is_loaded: return
        
        # Otherwise, import all modules.
        self._import_all_modules_()
        
        # Debug action.
        self.__logger__.debug(f"{self._name_} registry has been loaded")
        
        # Update status.
        self._loaded_:  bool =  True
        
    def register(self,
        name:   str,
        **kwargs
    ) -> None:
        """# Register Entry.

        ## Args:
            * name  (str):  Name of entry.
            
        ## Raises:
            * DuplicateEntryError:  If entry is already registered.
        """
        # If entry is already registered...
        if name in self._entries_:
            
            # Report error.
            raise DuplicateEntryError(entry_name = name, registry_name = self._name_)
        
        # Debug action.
        self.__logger__.debug(f"Registering {name} with arguments: {kwargs}")
        
        # Create & register entry.
        self._entries_[name] =  self._create_entry_(name = name, **kwargs)
        
    def register_parsers(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Argument Parsers.

        ## Args:
            * subparser (_SubParsersAction):    Command sub-parser of parent parser.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # For each registered entry...
        for entry in self._entries_.values():
            
            # If entry was registered with a parser handler...
            if entry.parser is not None:
                
                # Debug action.
                self.__logger__.debug(f"Registering arguments for {entry.name}")
                
                # Register parser.
                entry.register_parser(subparser = subparser)
        
    # HELPERS ======================================================================================
    
    @abstractmethod
    def _create_entry_(self, **kwargs) -> EntryType:
        """# Create Entry.
        
        Factory method to create the appropriate entry type for this registry.

        ## Returns:
            * EntryType:    New entry instance.
        """
        pass
    
    def _ensure_loaded_(self) -> None:
        """# Ensure Registry is Loaded."""
        if not self.is_loaded: self.load_all()
        
    def _import_all_modules_(self) -> None:
        """# Import All Modules."""
        from importlib  import import_module
        from pkgutil    import walk_packages
        from types      import ModuleType
        
        try:# Import the main package to get its path.
            package:    ModuleType =    import_module(f"lucidium.{self._name_}")
        
        # If import error occurs...
        except ImportError as e:
            
            # Warn of complications.
            self.__logger__.warning(f"Could not import package lucidium.{self._name_}: {e}")
            return
        
        # Debug action.
        self.__logger__.debug(f"Walking package: {package}")
        
        try:# For each module within package...
            for _, module, _ in walk_packages(
                path =      package.__path__,
                prefix =    f"lucidium.{self._name_}.",
                onerror =   lambda x: None
            ):
                
                try:# Attempt import of module.
                    import_module(name = module)
                    
                    # Debug action.
                    self.__logger__.debug(f"Walk of {module} complete")
                    
                # If import error occurs.
                except ImportError as e:
                    
                    # Warn of complications.
                    self.__logger__.warning(f"Error importing {module} module: {e}")
                    
        # If a package cannot be imported...
        except ImportError as e:
            
            # Warn of error.
            self.__logger__.warning(f"Error importing {package} package: {e}")
            
    # DUNDERS ======================================================================================
    
    def __contains__(self,
        key:    str
    ) -> bool:
        """# Registry Contains Entry?

        True if key is registered.
        """
        return key in self._entries_
    
    def __getitem__(self,
        key:    str
    ) -> Entry:
        """# Get Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.
            
        ## Raises:
            * KeyError: If entry is not registered.

        ## Returns:
            * Entry:    Entry requested.
        """
        return self.get_entry(key = key)
    
    def __len__(self) -> int:
        """# Number of Registrations."""
        return len(self._entries_)
    
    def __repr__(self) -> str:
        """# Registry Object Representation."""
        return f"""<{self._name_.capitalize()}Registry({len(self._entries_)} entries)>"""