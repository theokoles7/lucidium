"""# lucidium.protocol.interaciton.state

RL Interaction Protocol state enumeration.
"""

__all__ =   ["RLIPState"]

from enum   import Enum

class RLIPState(Enum):
    """# Reinforcement Learning Interaction Protocol State."""
    
    EPISODE_READY:      str =   "episode_ready"
    ERROR:              str =   "error"
    HANDSHAKE_PENDING:  str =   "handshake_pending",
    IN_EPISODE:         str =   "in_episode"
    LOADED:             str =   "loaded"
    NEGOTIATED:         str =   "negotiated"
    STEP_READY:         str =   "step_ready"
    TERMINATED:         str =   "terminated"
    UNINITIALIZED:      str =   "uninitialized"