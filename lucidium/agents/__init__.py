"""# lucidium.agents

This package defines various types of reinforcement learning agents.
"""

__all__ =   [
                # Abstract agent class.
                "Agent",
                
                # Concrete agent classes.
                "NeuralLogicMachine"
            ]

# Abstract agent class.
from lucidium.agents.__base__   import Agent

# Concrete agent classes.
from lucidium.agents.nlm        import NeuralLogicMachine