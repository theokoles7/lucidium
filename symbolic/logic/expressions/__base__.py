"""# lucidium.symbolic.logic.Expression

Define structure of logical expressions.
"""

__all__ = ["Expression"]

from abc                        import ABC, abstractmethod
from typing                     import Any, Dict, Set

from symbolic.logic.variable    import Variable
from symbolic.predicate.set     import PredicateSet

class Expression(ABC):
    """# Expression.
    
    Abstract class for logical expressions.
    """
    
    @abstractmethod
    def evaluate(self,
        predicate_set:  PredicateSet,
        bindings:       Dict[Variable, Any] =  None
    ) -> bool:
        """# Evaluate Logical Expression.
        
        Provide evaluation of logical expression.

        ## Args:
            * predicate_set (PredicateSet):                     Set of predicates that define 
                                                                evaluation constraints.
            * bindings      (Dict[Variable, Any], optional):    Expression variable bindings. 
                                                                Defaults to None.

        ## Returns:
            * bool:
                * True:     Expression is true.
                * False:    Expression is not true.
        """
        pass
    
    @abstractmethod
    def get_variables(self) -> Set[Variable]:
        """# Get Variables.
        
        Provide the variables on which expression depends.

        ## Returns:
            * Set[Variable]:   Set of expression's variables.
        """
        pass
    
    @abstractmethod
    def substitute(self,
        bindings:   Dict[Variable, Any]
    ) -> "Expression":
        """# Substitue Bindings.
        
        Substitue expression bindings.

        ## Args:
            * bindings  (Dict[Variable, Any]):  New expression variable bindings.

        ## Returns:
            * Expression:   New expression with substituted variable bindings.
        """
        pass
    
    @abstractmethod
    def to_cnf(self) -> "Expression":
        """# Convert to Conjunctive Normal Form.

        ## Returns:
            * Expression:   Logical expression in conjunctive normal form.
        """
        pass