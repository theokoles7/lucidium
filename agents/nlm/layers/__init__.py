"""# lucidium.agents.nlm.layers

This package defines the various layer components of the Neural Logic Machine.
"""

__all__ =   [
                "DimensionExpander",
                "DimensionPermuter",
                "DimensionReducer",
                "LinearLayer",
                "LogicLayer",
                "MLPLayer"
            ]

from agents.nlm.layers.expansion    import DimensionExpander
from agents.nlm.layers.permutation  import DimensionPermuter
from agents.nlm.layers.reduction    import DimensionReducer
from agents.nlm.layers.linear       import LinearLayer
from agents.nlm.layers.logic        import LogicLayer
from agents.nlm.layers.mlp          import MLPLayer