"""# lucidium.symbolic

This package defines various classes and utilities for use in neuro-symbolic reinforcement learning 
implementations.
"""

__all__ =   [
    
            # COMPOSITION
            
                # Components & taxonomies.
                "Candidate",
                "CompositionType",
                "Pattern",
                "PredicateSignature",
                
                # Composition execution, discovery, & validation.
                "CompositionEngine",
                "Validator"
            
            # LOGIC

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
    
            # PREDICATE
            
                # Predicate class.
                "Predicate",
                
                # Predicate components.
                "PredicateCategory",
                "PredicateSignature",
                "PredicateType",
                
                # Predicate structures.
                "PredicateSet",
                "PredicateVocabulary"
            ]

from symbolic.candidate     import *
from symbolic.composition   import *
from symbolic.logic         import *
from symbolic.predicate     import *