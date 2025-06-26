"""# lucidium.symbolic.logic.primitives.predicate

Core predicate representation.
"""

from typing import Tuple

class Predicate():
    """# Predicate
    
    Atomic symbolic predicate representing a relationship or property.
    
    Mathematical foundation: Atomic formulas in first-order logic of the form P(t1, t2, ..., tn) 
    where P is a predicate symbol and t1...tn are terms.
    
    ## Examples:
        * near(agent, block1)
        * color(block1, red)
        * movable(key)
    """
    
    def __init__(self,
        name:       str,
        arguments:  Tuple[str, ...],
        confidence: float =             1.0
    ):
        """# Instantiate Predicate.

        ## Args:
            * name          (str):              Name of the predicate (e.g., "near", "color", "movable").
            * arguments     (Tuple[str, ...]):  Tuple of argument names (e.g., ("agent", "block1")).
            * confidence    (float, optional):  Confidence score for the predicate. Defaults to 1.0.
        """
        # Define attributes.
        self._name_:        str =               name
        self._arguments_:   Tuple[str, ...] =   arguments
        self._confidence_:  float =             confidence
        
        # Validate parameters.
        self.__post_init__()
        
    def __post_init__(self) -> None:
        """# Validate Parameters.
        
        Ensure that proper parameters are provided for the predicate.
        
        ## Raises:
            * AssertionError: If the name is not a valid identifier.
        """
        # Assert that the name is a proper identifier.
        assert  isinstance(self._name_, str)                \
            and self._name_.isidentifier(),                 \
                "Predicate name must be a valid identifier.."
            
        # Assert that confidence is between 0.0 and 1.0.
        assert  isinstance(self._confidence_, float)        \
            and 0.0 <= self._confidence_ <= 1.0,            \
                f"Confidence must be a float between 0.0 and 1.0, got {self._confidence_}."
                
    # PROPERTIES ===================================================================================
    
    @property
    def arguments(self) -> Tuple[str, ...]:
        """# Arguments (Tuple[str, ...])
        
        Tuple of argument names for the predicate.
        """
        return self._arguments_
    
    @property
    def arity(self) -> int:
        """# Arity (int)
        
        Number of arguments the predicate takes.
        """
        return len(self.arguments)
    
    @property
    def confidence(self) -> float:
        """# Confidence (float)
        
        Confidence score for the predicate.
        """
        return self._confidence_
    
    @property
    def name(self) -> str:
        """# Name (str)
        
        Name of the predicate.
        """
        return self._name_
    
    # DUNDERS ======================================================================================
    
    def __str__(self) -> str:
        """# String Representation
        
        Returns a string representation of the predicate.
        
        ## Returns:
            * str: String representation in the form "name(arg1, arg2, ...)".
        """
        # Form argument string.
        arguments:  str =   ", ".join(self.arguments)
        
        # Form confidence string.
        confidence: str =   f" (confidence={self.confidence})" if self.confidence < 1.0 else ""
        
        # Return formatted string.
        return f"{self.name}({arguments}){confidence}"