"""# lucidium.symbolic.logic.expressions

This package defines the various types of expressions.
"""

__all__ =   [
                # Abstract expression class.
                "Expression",
                
                # Concrete expression classes.
                "CompoundExpression",
                "PredicateExpression"
            ]

# Abstract expression class.
from symbolic.logic.expressions.__base__    import Expression

# Concrete expression classes.
from symbolic.logic.expressions.compound    import CompoundExpression
from symbolic.logic.expressions.predicate   import PredicateExpression