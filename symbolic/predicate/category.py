"""# lucidium.symbolic.predicate.PredicateCategory

Define symbolic predicate categories.
"""

__all__ = ["PredicateCategory"]

from enum   import Enum

class PredicateCategory(Enum):
    """# Predicate Category.
    
    Symbolic predicate categories supported by Lucidium framework.
    """
    # Define predicate categories.
    ATTRIBUTE:  str =   "attribute"
    SPATIAL:    str =   "spatial"
    TEMPORAL:   str =   "temporal"
    FUNCTIONAL: str =   "functional"
    COMPOSITE:  str =   "composite"