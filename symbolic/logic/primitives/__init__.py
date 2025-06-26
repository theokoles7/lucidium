"""# lucidium.symbolic.logic.primitives

This module provides the basic building blocks for symbolic reasoning:
- Predicate:    Atomic symbolic relationships (e.g., near(agent, block))
- Experience:   Training data linking symbolic states to outcomes
"""

__all__ =   [
                "Experience",
                "Predicate",
            ]

from symbolic.logic.primitives.experience   import Experience
from symbolic.logic.primitives.predicate    import Predicate