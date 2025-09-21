"""# lucidium.registration.registries.environment_registry

Defines the environment registry system.
"""

__all__ = ["EnvironmentRegistry"]

from typing                         import Dict, override

from lucidium.registration.core     import Registry
from lucidium.registration.entries  import EnvironmentEntry

class EnvironmentRegistry(Registry):
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
        # Initialize registry.
        super(EnvironmentRegistry, self).__init__(name = name)
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def entries(self) -> Dict[str, EnvironmentEntry]:
        """# Registry Entries."""
        return self._entries_.copy()
        
    # HELPERS ======================================================================================
    
    @override
    def _create_entry_(self, **kwargs) -> EnvironmentEntry:
        """# Create Environment Entry.

        ## Returns:
            * EnvironmentEntry: New environment entry instance.
        """
        return EnvironmentEntry(**kwargs)
            
    # DUNDERS ======================================================================================
    
    @override
    def __getitem__(self,
        key:    str
    ) -> EnvironmentEntry:
        """# Get Environment Entry.

        ## Args:
            * key (str):    Name of environment entry being fetched.

        ## Returns:
            * EnvironmentEntry: Agent entry requested.
        """
        return self.get_entry(key = key)