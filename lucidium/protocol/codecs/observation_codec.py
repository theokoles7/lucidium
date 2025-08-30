"""# lucidium.protocol.codecs.observation_codec

Defines environment <-> agent observation codec.
"""

from typing                             import Any

from torch                              import device

from lucidium.protocol.specifications   import ObservationSpec

class ObservationCodec():
    """# Observation Codec.
    
    Transforms raw environment observations to agent-compatible formates according to the 
    specification agreed to between entities.
    """
    
    def __init__(self,
        spec:       ObservationSpec,
        to_device:  device =            "cpu"
    ):
        """# Instantiate Observation Codec.

        ## Args:
            * spec      (ObservationSpec):  Observation specification that dicatates what format 
                                            observations will be transformed into for the entity 
                                            that utilizes the codec.
            * to_device (device):           Hardware device upon which tensors will be placed (if 
                                            using tensors). Defaults to "cpu".
        """
        # Define properties.
        self._specification_:   ObservationCodec =  spec
        self._device_:          device =            to_device
        
    # METHODS ======================================================================================
    
    def encode(self,
        observation:    Any
    )