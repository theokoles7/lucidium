"""# lucidium.symbolic.logic.primitives.experience

Experience data structure for learning from agent interactions.
"""

from typing                                 import Any, Dict, Optional, Set

from symbolic.logic.primitives.predicate    import Predicate

class Experience():
    """# Experience
    
    Represents a training example linking symbolic states to outcomes.
    
    Mathematical foundation: Training data in supervised learning, where each example is a tuple 
    (state, outcome) mapping symbolic states to their corresponding outcomes.
    
    ## Examples:
        * (near(agent, block1), success)
        * (color(block1, red), failure)
        * (movable(key), success)
    """
    
    def __init__(self,
        predicates: Set[Predicate],
        success:    bool,
        metadata:   Optional[Dict[str, Any]] =  None
    ):
        """# Instantiate Experience.
        
        ## Args:
            * predicates    (Set[Predicate]):                       Set of predicates representing 
                                                                    the symbolic state.
            * success       (bool):                                 Outcome of the experience (e.g., 
                                                                    success or failure).
            * metadata      (Optional[Dict[str, Any]], optional):   Additional metadata about the 
                                                                    experience. Defaults to None.
        """
        # Define attributes.
        self._predicates_: Set[Predicate] = predicates
        self._success_:    bool =           success
        self._metadata_:   Optional[Dict[str, Any]] = metadata
        
    # PROPERTIES ===================================================================================
    
    @property
    def predicates(self) -> Set[Predicate]:
        """# Predicates (Set[Predicate])
        
        Returns the set of predicates representing the symbolic state of the experience.
        
        ## Returns:
            * Set[Predicate]: Set of predicates in the experience.
        """
        return self._predicates_
    
    @property
    def success(self) -> bool:
        """# Success (bool)
        
        Returns the outcome of the experience (e.g., success or failure).
        
        ## Returns:
            * bool: Outcome of the experience.
        """
        return self._success_
        
    # DUNDERS ======================================================================================
    
    def __str__(self) -> str:
        """# String Representation.
        
        Returns a string representation of the experience.
        
        ## Returns:
            * str: String representation of the experience.
        """
        # Form predicates string.
        predicates: str =   ", ".join(
                                str(p) 
                                for p 
                                in sorted(
                                    self._predicates_,
                                    key = lambda p: p.name
                                )
                            )
        
        # Form outcome string.
        outcome:    str =   "SUCCESS" if self._success_ else "FAILURE"
        
        # Return formatted string.
        return f"Exprience({outcome}): {{{predicates}}}"