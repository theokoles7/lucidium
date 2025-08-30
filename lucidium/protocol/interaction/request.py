"""# lucidium.protocol.interaction.request

RL Interaction Protocol request structure.
"""

from dataclasses                                import dataclass, field
from typing                                     import Any, Dict, Literal, Union

from lucidium.protocol.interaction.capabilities import ActionCapability, ObservationCapability

@dataclass
class HandshakeRequest():
    """# RLIP Handshake Request.
    
    Formal handshake request with capability requirements.
    """
    entity_type:                    Literal["agent", "environment"]
    entity_name:                    str
    required_observation_format:    ObservationCapability
    required_action_format:         ActionCapability
    supported_capabilites:          Union[ActionCapability, ObservationCapability]
    metadata:                       Dict[str, Any]                                  = field(default_factory = dict)