"""# lucidium.symbolic.composition.Pattern

Define a pattern template for composing predicates into higher level concepts.
"""

from dataclasses                import dataclass
from typing                     import List

from symbolic.composition.type  import CompositionType
from symbolic.predicate         import PredicateSignature

@dataclass(frozen = True)
class Pattern():
    """# Pattern.
    
    Defines a pattern template for composing predicates into higher-level concepts.
    
    This is essentially a "recipe" that describes how to combine basic predicates to create a new 
    composite predicate. The pattern includes:
        * What predicates to look for.
        * How they should be combined logically.
        * What the resulting predicate should look like.
        * Statistical thresholds for when to create the composition.
    
    ## Examples:
        * accessible_key(X) ← near(agent, X) ∧ color(X, red)
        * safe_path(X, Y) ← path(X, Y) ∧ ¬dangerous(X, Y)
        * reachable(X) ← ∃Y: (near(agent, Y) ∧ connects(Y, X))
        
    ## Attributes:
        * name                  (str):                  Human-readable name for this composition 
                                                        pattern.
        * composition_type      (CompositionType):      How the component predicates are combined 
                                                        logically.
        * component_patterns    (List[str]):            List of predicate patterns that form the 
                                                        composition.
        * result_signature      (PredicateSignature):   Signature of the new composite predicate.
        * confidence_threshold  (float):                Minimum confidence required to create this 
                                                        composition.
        * minimum_support       (int):                  Minimum number of instances needed to 
                                                        validate the pattern.
        * description           (str):                  Human-readable description of what this 
                                                        composition represents.
    """
    # Define attributes.
    name:                   str
    composition_type:       CompositionType
    component_patterns:     List[str]
    result_signature:       PredicateSignature
    confidence_threshold:   float =             0.8
    minimum_support:        int =               3
    description:            str =               ""
    
    def __post_init__(self):
        """# Validate composition patter after construction."""
        # If confidence threshold is not between 0 and 1...
        if not (0 <= self.confidence_threshold <= 1):
            
            # Raise error.
            raise ValueError(f"Confidence threshold expected to be in range 0-1, got {self.confidence_threshold}")
        
        # If minimum support is not at least one...
        if self.minimum_support < 1:
            
            # Raise error.
            raise ValueError(f"Minimum support must be at least 1, got {self.minimum_support}")