"""# lucidium.protocol.interaction.capabilities.observation

RL Interaction Protocol observation capability types.
"""

from enum   import Enum

class ObservationCapability(Enum):
    """# RLIP Observation Capability Type."""
    COORDINATE:     str =   "coordinate"
    INDEX:          str =   "index"
    PREDICATE:      str =   "predicate"
    MIXED:          str =   "mixed"
    ONEHOT:         str =   "onehot"
    TENSOR:         str =   "tensor"
    VECTOR:         str =   "vector"