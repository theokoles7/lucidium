"""# lucidium.protocol.interaction

Defines the protocol by which agent <-> environment interactions are conducted/managed.
"""

__all__ =   [
                # Capabilities.
                "ActionCapability",
                "ObservationCapability",
                
                # Contexts.
                "EpisodeContext",
                "StepContext",
                
                # Handshake messages.
                "HandshakeRequest",
                "HandshakeResponse",
                
                # Interaction state.
                "RLIPState"
            ]

from lucidium.protocol.interaction.capabilities import *
from lucidium.protocol.interaction.context      import *
from lucidium.protocol.interaction.request      import HandshakeRequest
from lucidium.protocol.interaction.response     import HandshakeResponse
from lucidium.protocol.interaction.state        import RLIPState