"""# lucidium.symbolic.predicate

This package defines the various symbolic predicate types, categories, and abstract classes.
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

# Predicate class.
from symbolic.predicate.__base__    import Predicate

# Predicate components.
from symbolic.predicate.category    import PredicateCategory
from symbolic.predicate.signature   import PredicateSignature
from symbolic.predicate.type        import PredicateType

# Predicate structures.
from symbolic.predicate.set         import PredicateSet
from symbolic.predicate.vocabulary  import PredicateVocabulary