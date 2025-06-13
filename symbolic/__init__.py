"""# lucidium.symbolic

This package defines various classes and utilities for use in neuro-symbolic reinforcement learning 
implementations.
"""

__all__ =   [
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

from symbolic.predicate import *