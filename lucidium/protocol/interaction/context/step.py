"""# lucidium.protocol.interaction.context.step

RL Interaction Protocol step context structure.
"""

from dataclasses    import dataclass, field
from typing         import Any, Dict

@dataclass
class StepContext():
    """# RLIP Step Context.
    
    Context manager for step lifecycle.
    """
    step_id:    int
    episode_id: int
    metadata:   Dict[str, Any] =    field(default_factory = dict)