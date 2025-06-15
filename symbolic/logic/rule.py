"""# lucidium.symbolic.logic.Rule

Define structure of logical rule representing antecedent -> consequent patterns.
"""

from typing                     import Any, Dict, List, Optional, Set

from symbolic.logic.expressions import Expression, PredicateExpression
from symbolic.logic.variable    import Variable
from symbolic.predicate         import Predicate, PredicateSet

class Rule():
    """# Rule.
    
    Represents a logical rule: antecedent -> consequent.
    
    Used for ingerence and predicate discovery.
    """
    
    def __init__(self,
        antecedent: Expression,
        consequent: Expression,
        confidence: float =         1.0,
        name:       Optional[str] = None
    ):
        """# Instantiate Logical Rule.

        ## Args:
            * antecedent    (Expression):               The precondition/trigger for which rule 
                                                        applies.
            * consequent    (Expression):               The outcome/result which rule's antecedent 
                                                        would cause/yield.
            * confidence    (float, optional):          Confidence in rule. Defaults to 1.0.
            * name          (Optional[str], optional):  Rule name. Defaults to None.
        """
        # Define attributes.
        self._antecedent_:  Expression =    antecedent
        self._consequent_:  Expression =    consequent
        self._confidence_:  float =         confidence
        self._name_:        str =           name if name else f"""rule_{id(self)}"""
        
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of rule.

        ## Returns:
            * str:  String representation of rule.
        """
        return f"""Rule({self.name}: {self})"""
        
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of rule.

        ## Returns:
            * str:  String representation of rule.
        """
        return f"""{self.antecedent} → {self.consequent}{f" [{self.confidence:.2f}]" if self.confidence < 1.0 else ""}"""
    
    def _enumerate_bindings_(self,
        variables:      Set[Variable],
        predicate_set:  PredicateSet
    ) -> List[Dict[Variable, Any]]:
        """# Enumerate Bindings.
        
        Enumerate possible variable bindings.

        ## Args:
            * variables     (Set[Variable]):    Variables used for bindings.
            * predicate_set (PredicateSet):     Set of predicates in which variables will be 
                                                grounded.

        ## Returns:
            * List[Dict[Variable, Any]]:    List of enumerated variable bindings.
        """
        # Initialize set of possible values.
        values: Set[Any] =  set()
        
        # For each predicate in set.
        for predicate in predicate_set:
            
            # Extract all possible values from the predicate set.
            values.update(predicate.arguments)
            
        # TODO: This will use all combinations for now, which is exponential. In practive, we want 
        # to use constrain propagation and smart search.
        # If there is only one variable...
        if len(variables) == 1:
            
            # Extract variable.
            variable:   Variable =  next(iter(variables))
            
            # Return variable bindings for which antecedent is true.
            return  [
                        {variable:  value}
                        for variable, value
                        in values
                        if  self.antecedent.evaluate(
                                predicate_set = predicate_set,
                                bindings =      {variable: value}
                            )
                    ]
            
        # TODO: This will need a proper unification algorithm.
        # Otherise, simply return empty list.
        return []
    
    def _find_bindings_(self,
        predicate_set:  PredicateSet
    ) -> List[Dict[Variable, Any]]:
        """# Find Bindings.
        
        Provide all variable bindings that satisfy antecedent.

        ## Args:
            * predicate_set (PredicateSet): Set of predicates being evaluated under antecedent.

        ## Returns:
            * List[Dict[Variable, Any]]:    Variable bindings that satisfy antecedent.
        """
        # If there are no variables...
        if not self.antecedent.get_variables():
            
            # If antecendent is true for predicate set.
            if  self.antecedent.evaluate(predicate_set = predicate_set):
                
                # Return empty variable set.
                return [{}]
            
            # Otherwise, return empty list.
            return []
        
        # Otherise, return enumerated bindings of variables.
        return  self._enumerate_bindings_(
                    variables =     self.antecedent.get_variables(),
                    predicate_set = predicate_set
                )
        
    @property
    def antecedent(self) -> Expression:
        """# Get Antecedent.
        
        Provide antecendent expression of rule.

        ## Returns:
            * Expression:   Rule's antecedent.
        """
        return self._antecedent_
    
    def apply(self,
        predicate_set:  PredicateSet
    ) -> List[Predicate]:
        """# Apply Rule.
        
        Apply rule to predicate set.

        ## Args:
            * predicate_set (PredicateSet): Predicate set being applied to rule.

        ## Returns:
            * List[Predicate]:  List of predicates formed from rule and predicate set.
        """
        # Initialize list of derived predicates.
        predicates: List[Predicate] =   []
        
        # For each binding in list...
        for bindings in self._find_bindings_(predicate_set = predicate_set):
            
            # Apply bindings to concequent.
            grounded_consequent:    Expression =    self.consequent.substitute(
                                                        bindings =  bindings
                                                    )
            
            # If grounded consequent is a predicate expression...
            if isinstance(grounded_consequent, PredicateExpression):
                
                # Extract the predicate.
                predicate:  Predicate = grounded_consequent._predicate_
                
                # Adjust confidence.
                predicate:  Predicate = Predicate(
                                            name =          predicate.name,
                                            arguments =     predicate.arguments,
                                            signature =     predicate.signature,
                                            confidence =    predicate.confidence * self.confidence
                                        )
                
                # If predicate has not already been discovered, append it to derivation list.
                if not predicate_set.contains(predicate = predicate): predicates.append(predicate)
                
        # Provide derived predicates.
        return predicates
    
    @property
    def confidence(self) -> float:
        """# Get Confidence.
        
        Provide confidence of rule.

        ## Returns:
            * float:    Rule's confidence.
        """
        return self._confidence_
    
    @property
    def consequent(self) -> Expression:
        """# Get Consequent.
        
        Provide consequent expression of rule.

        ## Returns:
            * Expression:   Rule's consequent.
        """
        return self._consequent_
    
    def get_variables(self) -> Set[Variable]:
        """# Get Variables.
        
        Get all variables in this rule for which antecedent or consequent is true.

        ## Returns:
            * Set[Variable]:    Set of rule variables.
        """
        return self.antecedent.get_variables() | self.consequent.get_variables()
    
    @property
    def name(self) -> str:
        """# Get Name.
        
        Provide rule name.

        ## Returns:
            * str:  Name of rule.
        """
        return self._name_