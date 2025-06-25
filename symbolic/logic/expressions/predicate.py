"""# lucidium.symbolic.logic.expressions.PredicateExpression

Define structure of predicate expressions.
"""

from typing                                 import Any, Dict, Set

from symbolic.logic.expressions.__base__    import Expression
from symbolic.logic.variable                import Variable
from symbolic.predicate                     import Predicate, PredicateSet

class PredicateExpression(Expression):
    """# Predicate Expression.
    
    Single predicate as a logical expression.
    """
    
    def __init__(self,
        predicate:  Predicate
    ):
        """# Instantiate Predicate Expression.

        ## Args:
            * predicate (Predicate):    Predication on which expression will be constrained.
        """
        # Define predicate.
        self._predicate_:   Predicate = predicate
        
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate expression.

        ## Returns:
            * str:  String representation of predicate expression.
        """
        return f"""PredicateExpression({self._predicate_})"""
        
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate expression.

        ## Returns:
            * str:  String representation of predicate expression.
        """
        return str(self._predicate_)
        
    def evaluate(self,
        predicate_set:  PredicateSet,
        bindings:       Dict[Variable, Any] =  None
    ) -> bool:
        """# Evaluate Expression.

        ## Args:
            * predicate_set (PredicateSet):                         Set of predications on which 
                                                                    expression will be evaluated.
            * bindings      (Dict[LogicVariable, Any], optional):   Variable bindings which will be 
                                                                    evaluated in expression. 
                                                                    Defaults to None.

        ## Returns:
            * bool:
                * True:     Variable bindings satisfy predicate constraints.
                * False:    Variable bindings do not satisfy predicate constraints.
        """
        # If bindings were provided...
        if bindings is not None:
            
            # Return evaluation based on predicate grounded by variable bindings.
            return  predicate_set.contains(
                        predicate = self._predicate_.ground(
                                        bindings =  {
                                                        str(variable): value 
                                                        for variable, value 
                                                        in bindings.items()
                                                    }
                                    )
                    )
            
        # Otherwise, simply indicate that predicate exists in set.
        return predicate_set.contains(predicate = self._predicate_)
    
    def get_variables(self) -> Set[Variable]:
        """# Get Variables.
        
        Provide set of variables composed in expression.

        ## Returns:
            * Set[Variable]:    Set of variables.
        """
        return  set([
                        argument
                        for argument
                        in self._predicate_.arguments
                        if isinstance(argument, Variable)
                ])
        
    def substitute(self,
        bindings:   Dict[Variable, Any]
    ) -> "PredicateExpression":
        """# Substitue Bindings.
        
        Substitue expression bindings.

        Args:
            * bindings  (Dict[Variable, Any]):  New expression variable bindings.

        ## Returns:
            * PredicateExpression:  New expression with substituted variable bindings.
        """
        return  PredicateExpression(
                    predicate = Predicate(
                                    name =          self._predicate_.name,
                                    arguments =     (
                                                        bindings[arg] 
                                                            if isinstance(arg, Variable) 
                                                                and arg in bindings
                                                            else arg
                                                        for arg
                                                        in self._predicate_.arguments
                                                    ),
                                    signature =     self._predicate_.signature,
                                    confidence =    self._predicate_.confidence
                                )
                )
        
    def to_cnf(self) -> "PredicateExpression":
        """# Convert to Conjunctive Normal Form.

        ## Returns:
            * Expression:   The same expression, as predicate expressions will already be in CNF.
        """
        return self