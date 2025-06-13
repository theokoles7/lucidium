"""# lucidium.symbolic.predicate.PredicateSignature

Define structure and constraints of a predicate.
"""

__all__ = ["PredicateSignature"]

from dataclasses                    import dataclass
from typing                         import Any, List

from symbolic.predicate.category    import PredicateCategory
from symbolic.predicate.type        import PredicateType

@dataclass(frozen = True)
class PredicateSignature():
    """# Predicate Signature.
    
    Defines the structure and constraints of a predicate.
    
    ## Examples:
        * color(object, color_value) -> PredicateSignature("color", ["object", "color_value"])
        * near(object1, object2) -> PredicateSignature("near", ["object", "object"])
    """
    # Define parameters.
    name:           str
    arg_types:      List[str]
    category:       PredicateCategory = PredicateCategory.ATTRIBUTE
    description:    str =               ""
    
    @property
    def arity(self) -> int:
        """# Get Arity.
        
        Provide the arity of the predicate.

        ## Returns:
            * int:  Arity of predicate.
        """
        return len(self.arg_types)
    
    @property
    def type(self) -> PredicateType:
        """# Get Type.
        
        Provide the predicate's type.

        ## Returns:
            * PredicateType:    Predicate's type.
        """
        # Match arity.
        match self.arity:
            
            # Unary.
            case 1: return PredicateType.UNARY
            
            # Binary.
            case 2: return PredicateType.BINARY
            
            # Ternary.
            case 3: return PredicateType.TERNARY
            
            # N-ary.
            case _: return PredicateType.N_ARY
            
    def validate_arguments(self,
        arguments:  List[Any]
    ) -> bool:
        """# Validate Arguments.
        
        Vaidate that arguments match the expected types.

        ## Args:
            * arguments (List[Any]):    Arguments being validated.

        ## Returns:
            * bool:
                * True:     Arguments are valid for predicate.
                * False:    Arguments are not valid for predicate. 
        """
        return len(arguments) != self.arity