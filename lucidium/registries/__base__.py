"""# lucidium.registries.base

Defines the abstract registry system.
"""

from typing import Callable, Dict, List, Optional, Type

from .entry import RegistryEntry

class Registry():
    """# Registry
    
    Abstract registry system.
    """
    
    def __init__(self,
        name:   str
    ):
        """# Instantiate Registry
        
        ## Args:
            * name  (str):  Name of the sub-module that the registry represents (e.g., "agents", 
                            "environments")
        """
        # Define sub-module name.
        self._name_:    str =                       name
        
        # Initialize entry map.
        self._entries_: Dict[str, RegistryEntry] =  {}
        
    # PROPERTIES ===================================================================================
    
    @property
    def entries(self) -> Optional[Dict[str, RegistryEntry]]:
        """# Registry Entries"""
        return {name: entry.cls for name, entry in self._entries_.items()}
    
        
    # METHODS ======================================================================================
    
    def all(self) -> Optional[Dict[str, RegistryEntry]]:
        """# Registry Entries"""
        return self.entries
    
    def discover_submodules(self) -> None:
        """# Discover Sub-Modules.
        
        Automatically discover sub-module registrations by crawling the sub-package.
        """
        from importlib  import import_module
        from pkgutil    import walk_packages
        from types      import ModuleType
        
        # Discover modules.
        for _, module_name, _ in walk_packages(path = None, prefix = f"{self._name_}."): import_module(name = module_name)
    
    def get(self,
        key:    str
    ) -> RegistryEntry:
        """# Get Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * RegistryEntry:    Registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key].cls
    
    def list(self,
        filter_by:  Optional[List[str]] =   []
    ) -> Optional[List[str]]:
        """# List Entries.

        ## Args:
            * filter_by (Optional[List[str]], optional):    Tags by which entries will be filtered.

        ## Returns:
            * Optional[List[str]]:  List of entry names that satisfy tag filter(s).
        """
        return  [
                    name for name, entry 
                    in self._entries_.items() 
                    if  all(
                            tag in entry.tags
                            for tag in filter_by
                        )
                ]
    
    def register(self,
        cls:    Type,
        name:   str,
        tags:   Optional[List[str]] =   [],
        parser: Optional[Callable] =    None
    ) -> None:
        """# Register (Type).

        ## Args:
            * cls       (Type):                 Class being registered.
            * name      (str):                  Name of entry.
            * tags      (Optional[List[str]]):  Tags that describe the taxonomy of the class being registered.
            * parser    (Optional[Callable]):   Argument parser handler.
                                                        
        ## Raises:
            * ValueError:   If entry already exists.
        """
        # Assert that entry does not already exist.
        if name in self._entries_: raise ValueError(f"{name} if already registered.")
        
        # Register entry.
        self._entries_[name] =  RegistryEntry(
                                    cls =       cls,
                                    name =      name,
                                    tags =      tags,
                                    parser =    parser
                                )
        
    # DUNDERS ======================================================================================
    
    def __getitem__(self,
        key:    str
    ) -> RegistryEntry:
        """# Get Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * RegistryEntry:    Registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key].cls