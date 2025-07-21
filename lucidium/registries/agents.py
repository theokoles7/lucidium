"""# lucidium.registries.agents

Defines the agent registry.
"""

from typing     import Callable, List, Optional, Type

from .__base__  import Registry

AGENT_REGISTRY: Registry = Registry(name = "agents")

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