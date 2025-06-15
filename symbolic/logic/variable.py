"""# lucidium.symbolic.logic.Variable

Define representation of logical variables that can be bound to concrete values.
"""

__all__ = ["Variable"]

from dataclasses    import dataclass
from typing         import Optional

@dataclass(frozen = True)
class Variable():
    """# Variable.
    
    Represents a logical variable that can be bound to concrete values.
    """
    
    # Define parameters.
    name:           str
    variable_type:  Optional[str] = None
    
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of variable.

        ## Returns:
            * str:  String representation of variable.
        """
        return f"""?{self.name}"""
    
    def __hash__(self) -> int:
        """# Get Hash.
        
        Provide hash of variable.

        ## Returns:
            * int:  Variable hash.
        """
        return hash(self.name)