"""# lucidium.protocol.specification.observation_specification

Defines environment <-> agent observation specifications.
"""

__all__ = ["ObservatinoSpec"]

from dataclasses    import dataclass
from functools      import cached_property
from typing         import Literal, Optional, Tuple

from torch          import dtype, float32

@dataclass(frozen = True)
class ObservationSpec():
    
    # Define properties.
    mode:       Literal["image", "index", "one_hot", "vector"]
    shape:      Tuple[int, ...]
    size:       Optional[int] =                                 None
    data_type:  dtype =                                         float32
    
    # PROPERTIES ===================================================================================
    
    @cached_property
    def flattened_dimension(self) -> int:
        """# Flattened Dimension.

        Scalar size of observation when flattened to one dimension.
        """
        # Initialize size to 1.
        size:   int =   1
        
        # For each dimension, multiply by the size of that dimension.
        for dimension_size in self.shape: size *= dimension_size
        
        # Provide flattened size.
        return size
    
    # METHODS ======================================================================================
    
    def is_compatible_with(self,
        other_spec: "ObservationSpec"
    ) -> bool:
        """# Evaluate Compatibility.
        
        Evaluate is ObservationSpec objects are compatible.

        ## Args:
            * other_spec    (ObservationSpec):  ObservationSpec object being compared to this one.

        ## Returns:
            * bool: True if specs are of the same mode and have the same flattened dimension size.
        """
        # If `other_spec` is not an ObservationSpec object, they are not equal by default.
        if not isinstance(other_spec, ObservationSpec): return False
        
        # Otherwise, simply indicate that modes and flattened dimension sizes are equal.
        return  self.mode == other_spec.mode and \
                self.flattened_dimension == other_spec.flattened_dimension
    
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other:  "ObservationSpec"
    ) -> bool:
        """# Evaluate Equality.
        
        Evaluate if ObservationSpec objects are equal.

        ## Args:
            * other (ObservationSpec):  ObservationSpec object being compared to this one.

        ## Returns:
            * bool: True if all properties of ObservationSpec objects are equal.
        """
        # If `other` is not an ObservationSpec object, they are not equal by default.
        if not isinstance(other, ObservationSpec): return False
        
        # Otherwise, simply indicate that properties are equal between objects.
        return  all([
                    self.mode       == other.mode,
                    self.shape      == other.shape,
                    self.size       == other.size,
                    self.data_type  == other.data_type
                ])