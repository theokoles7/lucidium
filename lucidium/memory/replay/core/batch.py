"""# lucidium.memory.replay.core.batch

Standard experience replay batch structure.
"""

__all__ = ["Batch"]

from dataclasses                            import dataclass
from typing                                 import List, Optional

from numpy.typing                           import NDArray

from lucidium.memory.replay.core.transition import Transition

@dataclass(frozen = True)
class Batch():
    r"""# :class:`Batch`
    
    A sampled batch with optional indices and importance-sampling weights.
    
    ## Properties:
    * :param:`transitions`  (List[Transition]): Transitions sampled from buffer.
    * :param:`indices`      (NDArray | None):   Index ordering for transition samples.
    * :param:`importance`   (NDArray | None):   Weights representing the "importance" of each 
                                                transition sample.
    """
    transitions:    List[Transition]
    indices:        Optional[NDArray] = None
    importance:     Optional[NDArray] = None
    
    # DUNDERS ======================================================================================
    
    def __len__(self) -> int:
        """# Length of Transition Batch."""
        return len(self.transitions)