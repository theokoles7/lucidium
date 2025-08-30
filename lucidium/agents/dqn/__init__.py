"""# lucidium.agents.dqn

This package implements the Deep Q-Network agent proposed in the 2013 paper by Mnih et. al.
"""

__all__ =   [
                # Agent class.
                "DeepQNetwork",
                
                # Main process.
                "main"
            ]

# Agent class.
from lucidium.agents.dqn.__base__           import DeepQNetwork

# Entry point.
from lucidium.agents.q_learning.__main__    import main