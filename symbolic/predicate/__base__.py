"""# lucidium.symbolic.Predicate

Define the structure and function of a symbolic predicate.
"""

__all__ = ["Predicate"]

from dataclasses                    import dataclass
from hashlib                        import md5
from typing                         import Any, Dict, Optional, Tuple

from symbolic.predicate.signature   import PredicateSignature

@dataclass(frozen = True)
class Predicate():
    """# Predicate.
    
    A concrete predicate instance with specific arguments.
    
    ## Examples:
        * color(block1, red) -> Predicate("color", ["block1", "red"])
        * near(agent, door) -> Predicate("near", ["agent", "door"])
    """
    # Define parameters.
    name:       str
    arguments:  Tuple[Any, ...]
    signature:  Optional[PredicateSignature] =  None
    confidence: float =                         1.0
    
    def __post_init__(self):
        """# Validate construction of predicate."""
        # If signature was provided and their invalid...
        if self.signature is not None and not self.signature.validate_arguments(arguments = list(self.arguments)):
            
            # Raise error to report.
            raise ValueError(f"Arguments {self.arguments} don't match signature {self.signature}")
        
        # Assert that confidence is within range.
        assert 0.0 <= self.confidence <= 1.0, f"Confidence expected to be 0.0-1.0, got {self.confidence}"
        
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate.

        ## Returns:
            * str:  String representation of predicate.
        """
        return self.__str__()
        
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate.

        ## Returns:
            * str:  String representation of predicate.
        """
        return  f"""{self.name}({",".join(str(arg) for arg in self.arguments)}){f"[{self.confidence:.2f}]" if self.confidence < 1.0 else ""}"""
        
    @property
    def arity(self) -> int:
        """# Get Arity.
        
        Provide the arity of the predicate.
        
        ## Returns:
            * int:  Predicate arity.
        """
        return len(self.arguments)
        
    def ground(self,
        bindings:   Dict[str, Any]
    ) -> "Predicate":
        """# Ground Predicate.
        
        Apply variable bindings to create a grounded predicate.

        ## Arguments:
            * bindings  (Dict[str, Any]):   Variable bindings.

        ## Returns:
            * Predicate:    Grounded predicate.
        """
        return  Predicate(
                    name =          self.name,
                    arguments =          tuple(bindings.get(arg, arg) for arg in self.arguments),
                    signature =     self.signature,
                    confidence =    self.confidence
                )
    
    @property
    def hash_key(self) -> str:
        """# Get Hash Key.
        
        Provide unique hash for the predicate.

        ## Returns:
            * str:  Predicate's unique hash.
        """
        return  md5(
                    f"""{self.name}({",".join(str(arg) for arg in self.arguments)})""".encode()
        ).hexdigest()[:8]