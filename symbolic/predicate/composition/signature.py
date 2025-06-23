"""# lucidium.symbolic.composition.CompositePredicateSignature

Extend predicate signature for composite predicates.
"""

from typing             import Any, Dict, List

from symbolic.logic     import Expression
from symbolic.predicate import PredicateCategory, PredicateSignature

class CompositePredicateSignature(PredicateSignature):
    """# Composite Predicate Signature.

    Extend predicate signature for composite predicates.

    This extends the basic PredicateSignature to include information about how the composite 
    predicate is constructed from simpler ones. This is crucial for:
        * Understanding the hierarchical structure
        * Debugging why a composition was created
        * Transferring knowledge to new domains
        * Explaining agent reasoning to humans
    """

    def __init__(self,
        name:                   str,
        argument_types:         List[str],
        component_predicates:   List[PredicateSignature],
        definition:             Expression,
        category:               PredicateCategory =         PredicateCategory.COMPOSITE,
        description:            str =                       ""
    ):
        """# Instantiate Composite Predicate Signature.

        ## Args:
            * name                  (str):                          Signature name/identifier.
            * argument_types        (List[str]):                    Argument types applicable to 
                                                                    definition.
            * component_predicates  (List[PredicateSignature]):     The simpler predicates that make 
                                                                    up this composite.
            * definition            (Expression):                   Formal logical definition of the 
                                                                    composition.
            * category              (PredicateCategory, optional):  Category to which signature 
                                                                    applies. Defaults to 
                                                                    PredicateCategory.COMPOSITE.
            * description           (str, optional):                Signature description. Defaults 
                                                                    to "".
        """
        # Initialize predicate signature.
        super(CompositePredicateSignature, self).__init__(
            name =          name,
            arg_types =     argument_types,
            category =      category,
            description =   description
        )

        # Define attributes.
        self._component_predicates_:    List[PredicateSignature] =  component_predicates
        self._definition_:              Expression =                definition
        
        # Initialize context.
        self._creation_context_:        Dict[str, Any] =            {}

        # Initialize statistics.
        self._usage_statistics_:        Dict[str, Any] =            {
                                                                        "used":                 0,
                                                                        "success_rate":         0.0,
                                                                        "average_confidence":   0.0
                                                                    }
        
    def get_complexity(self) -> int:
        """# Get Complexity.

        Calculate the complexity of this composite predicate.
        
        Complexity is measured as the total number of basic predicates involved in the composition, 
        including nested compositions. This helps prioritize simpler compositions and understand the 
        hierarchical depth.

        ## Returns:
            * int:  Number of basic predicates
        """
        # Provide the sum of...
        return  sum(
                    # Number of components in composite signatures...
                    component.get_complexity()
                        if isinstance(component, CompositePredicateSignature)
                        
                        # And regular signatures...
                        else 1
                        
                    # For each component...
                    for component
                    
                    # In this signature.
                    in self._component_predicates_
                )
        
    def get_hierarchy_depth(self) -> int:
        """# Get Hierarchy Depth.
        
        Calculate (recursively) the maximum hierarchy depth of this composition.
        
        Depth represents how many levels of composition are involved:
            * Basic predicates have depth 0.
            * Compositions of basic predicates have depth 1.
            * Compositions of compositions have depth 2, etc.

        ## Returns:
            * int:  Maximum hierarchy depth.
        """
        # If composition has no components, depth is zero.
        if not self._component_predicates_: return 0
        
        # Return the max between...
        return  max(
                    # The maximum depth found for any composite components.
                    max(
                        component.get_hierarchy_depth()
                        for component
                        in self._component_predicates
                        if isinstance(component, CompositePredicateSignature)
                    ),
                    
                    # Depth of one if no composite components.
                    1
                )