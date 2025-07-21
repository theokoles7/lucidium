"""# lucidium.registries.environments

Defines the environment registry.
"""

from typing     import Callable, List, Optional, Type

from .__base__  import Registry

ENVIRONMENT_REGISTRY: Registry = Registry(name = "environments")

def register_environment(
    name:   str,
    tags:   Optional[List[str]] =   []
) -> Callable:
    """# Register Environment.

    ## Args:
        * name  (str):                              Name of environment registration entry.
        * tags  (Optional[List[str]], optional):    Tags that describe the environment's taxonomy.

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
        # Register environment.
        ENVIRONMENT_REGISTRY.register(
            name =  name,
            cls =   cls,
            tags =  tags
        )
        
        # Return registered class.
        return cls
    
    # Expose decorator.
    return decorator