"""# lucidium.symbolic.predicates.PredicateType

Define symbolic predicate types.
"""

__all__ = ["PredicateType"]

from enum   import Enum

class PredicateType(Enum):
    """# Predicate Type.
    
    Symbolic predicate types supported by Lucidium framework.
    """
    # Define predicate types.
    UNARY:      str =   "unary"
    BINARY:     str =   "binary"
    TERNARY:    str =   "ternary"
    N_ARY:      str =   "n_ary"