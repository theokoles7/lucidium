"""# lucidium.memory.transition

Standard reinforcement learning transition implementation.
"""

__all__ = ["Transition"]

from collections    import namedtuple

Transition =    namedtuple(
                    typename =      "Transition",
                    field_names =   [
                                        "old_state",
                                        "action",
                                        "reward",
                                        "new_state",
                                        "done"
                                    ]
                )