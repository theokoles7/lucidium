"""# lucidium.registries

This package defines the agent & environment registration systems.
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

# ClassRegistry & component classes.
from lucidium.registries.agent_entry            import AgentEntry
from lucidium.registries.agent_registry         import AgentRegistry
from lucidium.registries.command_entry          import CommandEntry
from lucidium.registries.command_registry       import CommandRegistry
from lucidium.registries.environment_entry      import EnvironmentEntry
from lucidium.registries.environment_registry   import EnvironmentRegistry

# Agent Registries.
AGENT_REGISTRY:                 AgentRegistry =         AgentRegistry(name = "agents")
AGENT_COMMAND_REGISTRY:         CommandRegistry =       CommandRegistry(name = "agents")
ENVIRONMENT_REGISTRY:           EnvironmentRegistry =   EnvironmentRegistry(name = "environments")
ENVIRONMENT_COMMAND_REGISTRY:   CommandRegistry =       CommandRegistry(name = "environments")

# Registration decorators.
from lucidium.registries.decorators import  (
                                                register_agent,
                                                register_agent_command,
                                                register_environment,
                                                register_environment_command
                                            )