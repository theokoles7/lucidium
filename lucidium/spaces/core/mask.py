"""# lucidium.spaces.core.mask

Space sampling mask.
"""

__all__ = ["Mask"]

from typing         import TypeAlias

from numpy          import int8
from numpy.typing   import NDArray

# A Mask is an NDArray of binary digits.
Mask:   TypeAlias = NDArray[int8]