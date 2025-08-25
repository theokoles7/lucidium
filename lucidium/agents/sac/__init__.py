"""# lucidium.agents.sac

Soft Actor-Critic package.
"""

__all__ =   [
                # Agent class.
                "SoftActorCritic",
                
                # Components.
                "ExperienceReplayBuffer",
                
                # Networks
                "PolicyNetwork",
                "SoftQNetwork",
                "ValueNetwork",
            ]

# Agent class.
from lucidium.agents.sac.__base__       import SoftActorCritic

# Components.
from lucidium.agents.sac.replay_buffer  import ExperienceReplayBuffer

# Networks.
from lucidium.agents.sac.networks       import *