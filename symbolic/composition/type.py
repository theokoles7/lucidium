"""# lucidium.symbolic.composition.CompositionType

Define composition types.
"""

from enum   import Enum

class CompositionType(Enum):
    """#Composition Type.
    
    Symbolic expression composition types supported by Lucidium framework.
    
    ## Types:
        * CONJUNCTION:          P1 ∧ P2 ∧ ... ∧ Pn (all must be true)
        * DISJUNCTION:          P1 ∨ P2 ∨ ... ∨ Pn (at least one must be true)
        * NEGATION:             ¬P (opposite must be true)
        * CONDITIONAL:          P1 → P2 (if P1 then P2)
        * EXISTENTIAL:          ∃x: P(x) (there exists some x)
        * UNIVERSAL:            ∀x: P(x) (for all x)
        * TEMPORAL_SEQUENCE:    P1 then P2 (temporal ordering)
    """
    # Define composition types.
    CONJUNCTION:        str =   "conjunction"
    DISJUNCTION:        str =   "disjunction"
    NEGATION:           str =   "negation"
    CONDITIONAL:        str =   "conditional"
    EXISTENTIAL:        str =   "existential"
    UNIVERSAL:          str =   "universal"
    TEMPORAL_SEQUENCE:  str =   "temporal_sequence"