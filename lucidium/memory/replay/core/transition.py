"""# lucidium.memory.replay.core.transition

Standard reinforcement learning transition implementation.
"""

__all__ = ["Transition"]

from dataclasses    import dataclass
from typing         import Union

from numpy.typing   import NDArray

@dataclass(frozen = True)
class Transition():
    r"""# :class:`Transition`
    
    Data of a single agent <-> environment interaction step.
    
    ## Properties:
    * :param:`state`        (NDArray):          State prior to agent's action.
    * :param:`action`       (NDArray | int):    Action submitted by agent.
    * :param:`reward`       (float):            Reward yielded/penalty incurred by agent's chosen action.
    * :param:`next_state`   (NDArray):          State after agent's action is submitted.
    * :param:`done`         (bool):             True if :param:`next_state` is terminal.
    """
    state:      NDArray
    action:     Union[NDArray, int]
    reward:     float
    next_state: NDArray
    done:       bool