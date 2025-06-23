"""# lucidium.symbolic.composition

This package defines the various symbolic composition and reasoning functionality.
"""

__all__ =   [
                # Components & taxonomies.
                "CompositionType",
                "Pattern",
                "PredicateSignature",
                
                # Composition execution, discovery, & validation.
                "CompositionEngine",
                "Validator"
            ]

from symbolic.composition.pattern       import Pattern
from symbolic.composition.signature     import PredicateSignature
from symbolic.composition.type          import CompositionType

from symbolic.composition.engine        import CompositionEngine
from symbolic.composition.validation    import Validator