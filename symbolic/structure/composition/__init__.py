"""# lucidium.symbolic.structure.composition

Predicate composition engine for creating hierarchical symbolic structures.

This package orchestrates the complete hierarchical predicate discovery process:
    - Pattern discovery from experience data
    - Quality validation of discovered patterns  
    - Creation of composite predicates from validated patterns
    - Management of the discovered predicate hierarchy
"""

__all__ =   [
                "CompositionEngine",
            ]

from symbolic.structure.composition.engine  import CompositionEngine