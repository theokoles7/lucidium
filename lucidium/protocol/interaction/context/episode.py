"""# lucidium.protocol.interaction.context.episode

RL Interaction Protocol episode context structure.
"""

from dataclasses    import dataclass, field
from typing         import Any, Dict, Optional

class EpisodeContext():
    """# RLIP Episode Context.
    
    Context manager for episode lifecycle.
    """
    episode_id:     Optional[int]   = None
    metadata:       Dict[str, Any]  = field(default_factory = dict)