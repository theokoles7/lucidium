"""# lucidium.registries

This package defines the agent & environment registration systems.
"""

__all__ =   [
                # Registry & component classes.
                "Registry",
                "RegistryEntry",
                
                # Specific registries
                "AGENT_REGISTRY",
                "ENVIRONMENT_REGISTRY",
                
                # Registration decorators  
                "register_agent",
                "register_environment"
            ]

# Registry & component classes.
from .__base__      import Registry
from .entry         import RegistryEntry

# Registries.
AGENT_REGISTRY:         Registry =  Registry(name = "agents")
ENVIRONMENT_REGISTRY:   Registry =  Registry(name = "environments")

# Registration decorators 
from .decorators    import register_agent, register_environment