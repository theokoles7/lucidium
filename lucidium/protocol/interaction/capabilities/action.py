"""# lucidium.protocol.interaction.capabilities.action

RL Interaction Protocol action capability types.
"""

from enum   import Enum

class ActionCapability(Enum):
    """# RLIP Action Capability Type."""
    CONTINUOUS:     str =   "continuous"
    COORDINATE:     str =   "coordinate"
    INDEX:          str =   "index"
    TENSOR:         str =   "tensor"
    VECTOR:         str =   "vector"