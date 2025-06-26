"""# lucidium.symbolic.structure.patterns

Pattern discovery and analysis for hierarchical predicate discovery.

This package implements the core pattern mining algorithms that identify meaningful predicate 
combinations from experience data:

- Pattern: Data structure representing discovered predicate combinations
- PatternDiscovery: Algorithm for mining frequent, successful patterns
- Statistical analysis of predicate co-occurrences and success correlations

Mathematical foundation: Association rule mining and frequent itemset discovery applied to symbolic 
predicate data for automatic hierarchy construction.
"""

__all__ =   [
                # Pattern class.
                "Pattern",
                
                # Subsystems.
                "PatternDiscoverer",
            ]

# Pattern class.
from symbolic.structure.patterns.__base__   import Pattern

# Subsystems.
from symbolic.structure.patterns.discovery  import PatternDiscoverer