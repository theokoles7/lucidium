"""# lucidium.protocol.codecs.tests.observation_codec_test

Defines tests for the observation codec.
"""

from lucidium.protocol.codecs.observation_codec import ObservationCodec
from lucidium.protocol.specifications           import ObservationSpec

class TestObservationCodec():
    """# Observation Codec Test Suite."""
    
    def test_observation_codec_initialization(self):
        """# Test Observation Codec Initialization."""
        # Define a sample observation specification.
        spec:   ObservationSpec =   ObservationSpec(
                                        mode =      "index",
                                        shape =     (4, 4),
                                        size =      10,
                                        data_type = "int32"                                        
                                    )
        
        # Initialize the observation codec.
        codec:  ObservationCodec =  ObservationCodec(
                                        spec =      spec,
                                        to_device = "cpu"
                                    )
        
        # Assertions to verify correct initialization.
        assert codec._specification_ == spec,   f"Observation codec specification expected to be {spec}, got {codec._specification_}"
        assert codec._device_        == "cpu",  f"Observation codec device expected to be 'cpu', got {codec._device_}"