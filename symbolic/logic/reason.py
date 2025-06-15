"""# lucidium.symbolic.logic.reason

Define structure and functionality of logical reasoner.
"""

from typing                     import List

from symbolic.logic.expressions import Expression, PredicateExpression
from symbolic.logic.rule        import Rule
from symbolic.predicate         import Predicate, PredicateSet

class Reasoner():
    """# Reasoner.
    
    Performs logical reasoning operations on predicate sets.
    
    Supports forward chaining, backward chaining, and rule application.
    """
    
    def __init__(self):
        """# Instantiate Reasoner."""
        # Initialize list for storing rules.
        self._rules_:   List[Rule] =    []
        
    def add_rule(self,
        rule:   Rule
    ) -> None:
        """# Add Rule.
        
        Append rule to reasoner's list of rules.

        ## Args:
            * rule  (Rule): Rule being added.
        """
        self._rules_.append(rule)
        
    def clear_rule(self) -> None:
        """# Clear Rules.
        
        Empty reasoner's rule list.
        """
        self.rules.clear()
        
    def explain(self,
        query:          Expression,
        predicate_set:  PredicateSet
    ) -> List[str]:
        """# Explain.
        
        Provide an explanation for why a query is true or false.

        ## Args:
            * query         (Expression):   Query expression being evaluated.
            * predicate_set (PredicateSet): Predicate set on which expression will be evaluated.

        ## Returns:
            * List[str]:    List of reasoning steps.
        """
        # Initialize list of reasoning steps.
        explanation:    List[str] = []
        
        # TODO: This method is very simplified for now, just expressing if predicates exist in set.
        # This should be enhanced to provide actual reasoning steps.
        
        # If query is a predicate expression.
        if isinstance(query, PredicateExpression):
            
            # Simply indicate if predicate is present in set.
            explanation.append(
                f"""✓ {query.predicate} is directly present"""
                if predicate_set.contains(predicate = query._predicate_)
                else f"""✗ {query.predicate} is not present"""
            )
            
        # Provide reasoning steps.
        return explanation
        
    def forward_chain(self,
        predicate_set:  PredicateSet,
        max_iterations: int =           10
    ) -> PredicateSet:
        """# Forward Chain.
        
        Apply forward chaining to derive new predicates.

        ## Args:
            * predicate_set     (PredicateSet):     Initial set of predicates.
            * max_iterations    (int, optional):    Maximum number of inference iterations. Defaults 
                                                    to 10.

        ## Returns:
            * PredicateSet: Enhanced predicate set with derived predicates.
        """
        # Initialize new predicate set as copy of set provided.
        derived:    PredicateSet =  PredicateSet(
                                        predicates =    predicate_set.to_list()
                                    )
        
        # For each prescribed inference iteration...
        for iteration in range(max_iterations):
            
            # Initialize empty list of new predicates.
            new_predicates: List[Predicate] =   []
            
            # For each rule currently stored...
            for rule in self.rules:
                
                # Use rule to derive new predicates.
                new_predicates.extend(rule.apply(predicate_set = derived))
                
            # Initialize flag to indicate if predicates already existed in set.
            added:  bool =          False
                
            # For each new predicate...
            for predicate in new_predicates:
                
                # If rule is successfully added...
                if derived.add(predicate = predicate):
                    
                    # Set flag.
                    added =         True
                    
            # If no new predicates were added, chaining is complete.
            if not added: break
            
        # Return derived predicates.
        return derived
    
    def get_rule_count(self) -> int:
        """# Get Rule Count.
        
        Get number of rules in reasoner.

        ## Returns:
            * int:  Number of rules in reasoner.
        """
        return len(self.rules)
    
    def query(self,
        query:          Expression,
        predicate_set:  PredicateSet
    ) -> bool:
        """# Submit Query.
        
        Query if expression can be satisfied by the predicate set.
        
        Uses forward chaining to derive additional predicates if needed.

        ## Args:
            * query         (Expression):   Expression which will be tested by grounding predicate 
                                            set.
            * predicate_set (PredicateSet): Predicate set by which expression will be evaluated.

        ## Returns:
            * bool:
                * True:     Predicate set satisfies expression.
                * False:    Predicate set does not satisfy expression.
        """
        return  query.evaluate(
                    predicate_set = self.forward_chain(
                        predicate_set = predicate_set
                    )
                )
        
    @property
    def rules(self) -> List[Rule]:
        """# Get Rules.
        
        Provide rules stored in reasoner.

        ## Returns:
            * List[Rule]:   Reasoner's list of stored rules.
        """
        return self._rules_