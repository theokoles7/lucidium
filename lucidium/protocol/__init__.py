"""# lucidium.protocol

Defines control mechanismss for agent <-> environment interactions.
"""

__all__ =   [
                # Codecs.
                "ObservationCodec",
                
                # Interaction.
                "ActionCapability",
                "ObservationCapability",
                "EpisodeContext",
                "StepContext",
                "HandshakeRequest",
                "HandshakeResponse",
                "RLIPState",
                
                # Specifications.
                "ActionSpec",
                "ObservationSpec"
            ]

from lucidium.protocol.codecs           import *
from lucidium.protocol.interaction      import *
from lucidium.protocol.specifications   import *