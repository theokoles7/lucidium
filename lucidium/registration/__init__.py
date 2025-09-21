"""# lucidium.registration

This package defines registration systems and their utilities.
"""

__all__ =   [
                # Class Registry & component classes.
                "AgentEntry",
                "AgentRegistry",
                "EnvironmentEntry",
                "EnvironmentRegistry",
                
                # Command Registry & component classes.
                "CommandRegistry",
                "CommandEntry",
                
                # Specific registries
                "AGENT_REGISTRY",
                "AGENT_COMMAND_REGISTRY",
                "ENVIRONMENT_REGISTRY",
                "ENVIRONMENT_COMMAND_REGISTRY",
                
                # Registration decorators  
                "register_agent",
                "register_agent_command",
                "register_environment",
                "register_environment_command"
            ]

from lucidium.registration.core         import *
from lucidium.registration.entries      import *
from lucidium.registration.registries   import *

# Agent Registries.
AGENT_REGISTRY:                 AgentRegistry =         AgentRegistry(name = "agents")
AGENT_COMMAND_REGISTRY:         CommandRegistry =       CommandRegistry(name = "agents")
ENVIRONMENT_REGISTRY:           EnvironmentRegistry =   EnvironmentRegistry(name = "environments")
ENVIRONMENT_COMMAND_REGISTRY:   CommandRegistry =       CommandRegistry(name = "environments")