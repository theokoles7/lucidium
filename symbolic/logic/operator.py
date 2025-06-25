"""# lucidium.symbolic.logic.Operator

Define symbolic logic operators.
"""

__all__ = ["Operator"]

from enum   import Enum

class Operator(Enum):
    """# Logic Operator.
    
    Symbolic logic operators for combining predicates.
    """
    # Define logic operators.
    AND:        str =   "∧"
    OR:         str =   "∨"
    NOT:        str =   "¬"
    IMPLIES:    str =   "→"
    IFF:        str =   "↔"