"""# lucidium.registries.decorators

Registration decorators for agents/environments.
"""

__all__ = ["register_agent", "register_environment"]

from typing import Callable, List, Optional, Type

def register_agent(
    name:   str,
    tags:   Optional[List[str]] =   [],
    parser: Optional[Callable] =    None
) -> Callable:
    """# Register Agent.

    ## Args:
        * name      (str):                  Name of agent registration entry.
        * tags      (Optional[List[str]]):  Tags that describe the agent's taxonomy.
        * parser    (Optional[Callable]):   Agent's argument registration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        cls:    Type
    ) -> Type:
        """# Registration Decorator

        ## Args:
            * cls   (Type): Agent class being registered.
        """
        # Load registry.
        from . import AGENT_REGISTRY
        
        # Register agent.
        AGENT_REGISTRY.register(
            cls =       cls,
            name =      name,
            tags =      tags,
            parser =    parser
        )
        
        # Return registered class.
        return cls
    
    # Expose decorator.
    return decorator

def register_environment(
    name:   str,
    tags:   Optional[List[str]] =   [],
    parser: Optional[Callable] =    None
) -> Callable:
    """# Register Environment.

    ## Args:
        * name      (str):                  Name of environment registration entry.
        * tags      (Optional[List[str]]):  Tags that describe the environment's taxonomy.
        * parser    (Optional[Callable]):   Environment's argument registration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        cls:    Type
    ) -> Type:
        """# Registration Decorator

        ## Args:
            * cls   (Type): Environment class being registered.
        """
        # Load registry.
        from . import ENVIRONMENT_REGISTRY
        
        # Register environment.
        ENVIRONMENT_REGISTRY.register(
            cls =       cls,
            name =      name,
            tags =      tags,
            parser =    parser
        )
        
        # Return registered class.
        return cls
    
    # Expose decorator.
    return decorator