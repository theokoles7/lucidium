"""# lucidium.symbolic.patterns

Structural analysis and hierarchical discovery for symbolic reasoning.

This package implements algorithms for discovering and managing hierarchical
relationships in symbolic predicate data:

- patterns/: Pattern mining and co-occurrence analysis
- composition/: Hierarchical predicate creation and management
- Future: hierarchy management, validation, optimization

The structure package focuses on the mathematical and algorithmic aspects
of building symbolic hierarchies from experience data.
"""

__all__ =   [
                # Pattern analysis
                "Pattern",
                "PatternDiscovery", 
                
                # Composition engine
                "CompositionEngine"
            ]

from symbolic.structure.composition import *
from symbolic.structure.patterns    import *