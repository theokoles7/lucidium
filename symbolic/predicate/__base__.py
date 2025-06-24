"""# lucidium.symbolic.predicate.Predicate

A base class for symbolic predicates, which are used to represent logical conditions or 
relationships between variables in a neurosymbolic framework. This class provides a foundation for 
creating more complex predicates that can be used in reasoning tasks.
"""

from typing import Any, Dict, list, Tuple

class Predicate():
    """# Predicate

    A base class for symbolic predicates, which are used to represent logical conditions or 
    relationships between variables in a neurosymbolic framework. This class provides a foundation 
    for creating more complex predicates that can be used in reasoning tasks.
    
    ## Examples:
        * color(block1, red) -> Predicate("color", ("block1", "red"))
        * near(agent, door) -> Predicate("near", ("agent", "door"))
        * movable(box) -> Predicate("movable", ("box",))
    """
    
    def __init__(self,
            name:       str,
            arguments:  Tuple[Any, ...],
            confidence: float =             1.0,
        ):
        """# Initialize Predicate

        Initializes the predicate with default values or configurations.
        """
        # Assert that name is not empty.
        assert  isinstance(name, str)           and \
                name != "",                             "Predicate name must be a non-empty string."
        
        # Assert that confidence is between 0 and 1.
        assert  isinstance(confidence, float)   and \
                0.0 <= confidence <= 1.0,               "Confidence must be a float between 0.0 and 1.0."
                
        # If arguments is not a tuple, convert it to a tuple.
        if not isinstance(arguments, tuple):    arguments = tuple(arguments)
        
        # Define attributes.
        self._name_:        str =               name
        self._arguments_:   Tuple[Any, ...] =   arguments
        self._confidence_:  float =             confidence
        
    # PROPERTIES ===================================================================================
    
    @property
    def arguments(self) -> Tuple[Any, ...]:
        """# (Predicate) Arguments

        The arguments of the predicate, which are the variables or values involved in the logical 
        condition or relationship.
        """
        return self._arguments_
    
    @property
    def arity(self) -> int:
        """# (Predicate) Arity

        The number of arguments the predicate takes, which is useful for understanding its 
        complexity and how it interacts with other predicates.
        """
        return len(self._arguments_)
    
    @property
    def confidence(self) -> float:
        """# (Predicate) Confidence

        The confidence score of the predicate, which indicates the certainty of the logical 
        condition or relationship being true.
        """
        return self._confidence_
    
    @property
    def is_ground(self) -> bool:
        """# (Predicate) Is Ground?
        
        Indicates whether the predicate is ground, meaning it has no variables and all arguments
        are concrete values. This is useful for determining if the predicate can be evaluated
        directly without further variable resolution.
        
        ## Returns:
            * bool: True if the predicate is ground (has no variables), False otherwise.
        """
        return len(self.arguments) == 0
    
    @property
    def name(self) -> str:
        """# (Predicate) Name

        The name of the predicate, which represents the logical condition or relationship.
        """
        return self._name_
    
    @property
    def signiature(self) -> str:
        """# (Predicate) Signiature

        The signiature of the predicate, which is a string representation of the predicate's name 
        and its arguments. This is useful for identifying the predicate in a more human-readable 
        format.
        
        ## Returns:
            * str:  Signiature of the predicate.
        """
        return f"{self._name_}(arity={self.arity})"
    
    @property
    def variables(self) -> List[Any]:
        """# (Predicate) Variables

        The variables involved in the predicate's arguments. This is useful for understanding the 
        symbolic nature of the predicate and how it can be used in logical reasoning.
        
        ## Returns:
            * List[Any]:    A list of variables in the predicate's arguments.
        """
        return  [
                    argument
                    for argument
                    in self.arguments
                    if          hasattr(argument, 'name') 
                        and     str(argument).startswith('?')
                ]
    
    # METHODS ======================================================================================
    
    def ground(self,
        bindings:   Dict[Any, Any]
    ) -> "Predicate":
        """# (Predicate) Ground
        
        Grounds the predicate by replacing its arguments with the provided bindings. This is useful 
        for creating specific instances of the predicate with concrete values.
        
        ## Args:
            * bindings (Dict[Any, Any]):  A dictionary mapping variable names to their concrete values.
        
        ## Returns:
            * Predicate:  A new predicate instance with grounded arguments.
        """
        # Create a new predicate with grounded arguments.
        grounded_arguments: Tuple[Any] =    tuple(
                                                bindings.get(argument, argument)
                                                for argument
                                                in self._arguments_
                                                if argument in self.arguments
                                                else argument
                                            )
        
        # Return a new Predicate instance with the grounded arguments.
        return  Predicate(
                    name =          self.name,
                    arguments =     grounded_arguments,
                    confidence =    self.confidence
                )
        
    def matches_pattern(self,
        pattern:    "Predicate"
    ) -> bool:
        """# (Predicate) Matches Pattern?
        
        Checks if the predicate matches a given pattern. This is useful for determining if the
        predicate can be unified with the pattern, which is a common operation in symbolic 
        reasoning.
        
        ## Args:
            * pattern   (Predicate):    The pattern to match against.
            
        ## Returns:
            * bool: True if the predicate matches the pattern, False otherwise.
        """
        # 
        if self._name_  != pattern._name_:  return False
        if self.arity   != pattern.arity:   return False
        
        for self_arg, pattern_arg in zip(self._arguments_, pattern._arguments_):
            # If pattern arg is a variable, it matches anything.
            if hasattr(pattern_arg, 'name') and str(pattern_arg).startswith('?'):
                continue
            # Otherwise, arguments must be exactly equal.
            if self_arg != pattern_arg:
                return False
        
        return True
        
    # CLASS METHODS ================================================================================
    
    def with_confidence(self,
        confidence:  float
    ) -> "Predicate":
        """# (Predicate) With Confidence
        
        Creates a new predicate with the same name and arguments but with a specified confidence 
        score. This is useful for adjusting the certainty of the logical condition or relationship.
        
        ## Args:
            * confidence    (float):    The confidence score to set for the new predicate.
        
        ## Returns:
            * Predicate:    A new predicate instance with the specified confidence score.
        """
        # Return a new Predicate instance with the specified confidence.
        return  Predicate(
                    name =          self.name,
                    arguments =     self.arguments,
                    confidence =    confidence
                )
    
    # DUNDERS ======================================================================================
    
    def __eq__(self, other: Any) -> bool:
        """# (Predicate) Equality Check
        
        Checks if two predicates are equal based on their name, arguments, and confidence score.
        
        ## Args:
            * other (Any):  The other object to compare against.
        
        ## Returns:
            * bool: True if the predicates are equal, False otherwise.
        """
        return  all([
                    isinstance(other, Predicate),
                    self.name       == other.name,
                    self.arguments  == other.arguments,
                    self.confidence == other.confidence
                ])
        
    def __hash__(self) -> int:
        """# (Predicate) Hash
        
        Returns a hash value for the predicate, which is based on its name, arguments, and confidence.
        
        ## Returns:
            * int:  Hash value of the predicate.
        """
        return hash((self.name, self.arguments, self.confidence))
    
    def __repr__(self) -> str:
        """# (Predicate) String Representation
        
        Provides a detailed string representation of the predicate, including its name, arguments,
        and confidence score.

        ## Returns:
            * str:  Detailed representation.
        """
        return f"Predicate(name={self.name}, arguments={self.arguments}, confidence={self.confidence})"
    
    def __str__(self) -> str:
        """# (Predicate) String Representation
        
        Provides a concise string representation of the predicate, showing its name and arguments.
        
        ## Returns:
            * str:  Concise representation.
        """
        # Format the string representation of the predicate's arguments and confidence.
        arguments:  str =   ", ".join(str(arg) for arg in self._arguments_)
        confidence: str =   f"[{self._confidence_:.2f}]" if self._confidence_ < 1.0 else ""
        
        return f"{self._name_}({arguments}){confidence}"