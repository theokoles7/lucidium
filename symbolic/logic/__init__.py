"""# lucidium.symbolic.logic

This package defines the various symbolic logic operators and operations.
"""

__all__ =   [
                # Expressions.
                "Expression",
                "CompoundExpression",
                "PredicateExpression",
                
                # Logical expression components.
                "Operator",
                "Variable",
                
                # Expression structures.
                "Reasoner",
                "Rule"
]

# Expressions.
from symbolic.logic.expressions import *

# Logical expression components.
from symbolic.logic.operator    import Operator
from symbolic.logic.variable    import Variable

# Expression structures.
from symbolic.logic.reason      import Reasoner
from symbolic.logic.rule        import Rule