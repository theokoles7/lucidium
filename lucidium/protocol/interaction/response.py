"""# lucidium.protocol.interaction.response

RL Interaction Protocol response structure.
"""

from dataclasses                                import dataclass, field
from typing                                     import Any, Dict, Optional

from lucidium.protocol.interaction.capabilities import ActionCapability, ObservationCapability

@dataclass
class HandshakeResponse():
    """# RLIP Handshake Response.
    
    Formal handshake response with negotiated action/observation formats.+ 
    """
    accepted:                       bool
    negotiated_observation_format:  Optional[ObservationCapability]
    negotiated_action_format:       Optional[ActionCapability]
    compatibility_adapter:          Optional[Any]                   = None
    error_message:                  Optional[Any]                   = None
    metadata:                       Dict[str, Any]                  = field(default_factory = dict)