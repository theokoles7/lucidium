"""# lucidium.agents.sac.args

Argument definitions and parsing for Soft Actor-Critic agent.
"""

__all__ = ["register_sac_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction

from lucidium.registries    import AGENT_COMMAND_REGISTRY

def register_sac_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Soft Actor-Critic Argument Parser.
    
    Add SAC agent sub-parser & arguments to parent's sub-parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize Soft Actor-Critic Agent parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "sac",
        help =          "Soft Actor-Critic agent.",
        description =   """Soft Actor-Critic (SAC) is an off-policy actor-critic deep reinforcement 
                        learning algorithm based on the maximum entropy reinforcement learning 
                        framework. The actor aims to maximize expected reward while also maximizing 
                        entropy, succeeding at the task while acting as randomly as possible.""",
        epilog =        """Implementation based on "Soft Actor-Critic: Off-Policy Maximum Entropy 
                        Deep Reinforcement Learning with a Stochastic Actor" by Haarnoja et al. 
                        (2018). Link to paper: https://arxiv.org/pdf/1801.01290"""
    )
    
    # Initialize sub-parser.
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        dest =          "agent_action",
        help =          """Action that agent will execute."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # NETWORK ARCHITECTURE ================================================
    _architecture_:     _ArgumentGroup =    _parser_.add_argument_group(title = "Network Architecture")
    
    _architecture_.add_argument(
        "--actor-hidden-dimension",
        dest =          "actor_hidden_dimension",
        type =          int,
        nargs =         "+",
        default =       (256, 256),
        help =          """Hidden layer sizes for actor network(s). Defaults to (256, 256)."""
    )
    
    _architecture_.add_argument(
        "--critic-hidden-dimension",
        dest =          "critic_hidden_dimension",
        type =          int,
        nargs =         "+",
        default =       (256, 256),
        help =          """Hidden layer sizes for critic network(s). Defaults to (256, 256)."""
    )
    
    _architecture_.add_argument(
        "--value-hidden-dimension",
        dest =          "value_hidden_dimension",
        type =          int,
        nargs =         "+",
        default =       (256, 256),
        help =          """Hidden layer sizes for value network(s). Defaults to (256, 256)."""
    )
    
    # LEARNING RATE =======================================================
    _learning_:         _ArgumentGroup =    _parser_.add_argument_group("Learning Rate")
    
    _learning_.add_argument(
        "--actor-learning-rate", "--actor-lr",
        dest =          "actor_learning_rate",
        type =          float,
        default =       1e-3,
        help =          """Learning rate for actor network(s). Defaults to 0.001."""
    )
    
    _learning_.add_argument(
        "--critic-learning-rate", "--critic-lr",
        dest =          "critic_learning_rate",
        type =          float,
        default =       1e-3,
        help =          """Learning rate for critic network(s). Defaults to 0.001."""
    )
    
    _learning_.add_argument(
        "--value-learning-rate", "--value-lr",
        dest =          "value_learning_rate",
        type =          float,
        default =       1e-3,
        help =          """Learning rate for value network(s). Defaults to 0.001."""
    )
    
    # HYPERPARAMETERS =====================================================
    _hyperparameters_:  _ArgumentGroup =    _parser_.add_argument_group("Hyperparameters")
    
    _hyperparameters_.add_argument(
        "--discount-rate", "--dr", "--gamma",
        dest =          "discount_rate",
        type =          float,
        default =       0.99,
        help =          """Discount factor for future rewards. Defaults to 0.99."""
    )
    
    _hyperparameters_.add_argument(
        "--soft-update-coefficient", "--polyak-factor", "--tau",
        dest =          "soft_update_coefficient",
        type =          float,
        default =       5e-3,
        help =          """Soft update coefficient for target networks. Defaults to 0.005."""
    )
    
    _hyperparameters_.add_argument(
        "--temperature", "--alpha",
        dest =          "temperature",
        type =          float,
        default =       0.2,
        help =          """Temperature parameter for entropy regularization. Controls the relative 
                        importance of entropy term versus reward. Higher values encourage more 
                        exploration. Defaults to 0.2."""
    )
    
    _hyperparameters_.add_argument(
        "--auto-temperature", "--auto-alpha",
        dest =          "auto_temperature",
        action =        "store_true",
        default =       False,
        help =          """Whether to automatically tune the temperature parameter (alpha)."""
    )
    
    _hyperparameters_.add_argument(
        "--target-entropy",
        dest =          "target_entropy",
        type =          float,
        default =       None,
        help =          """Target entropy for automatic temperature tuning. If None, will be set to 
                        -action_dimension. Only used when auto_temperature is True."""
    )
    
    # REPLAY BUFFER =======================================================
    _buffer_:           _ArgumentGroup =    _parser_.add_argument_group("Experience Replay Buffer")
    
    _buffer_.add_argument(
        "--buffer-size",
        dest =          "buffer_size",
        type =          int,
        default =       1000000,
        help =          """Maximum capacity of experience replay buffer. Defaults to 1,000,000."""
    )
    
    _buffer_.add_argument(
        "--batch-size",
        dest =          "batch_size",
        type =          int,
        default =       256,
        help =          """Batch size for training process. Defaults to 256."""
    )
    
    # TRAINING ============================================================
    _training_:         _ArgumentGroup =    _parser_.add_argument_group("Training")
    
    _training_.add_argument(
        "--gradient-steps",
        dest =          "gradient_steps",
        type =          int,
        default =       1,
        help =          """Number of gradient steps per environment interaction. Defaults to 1."""
    )
    
    _training_.add_argument(
        "--exploration-steps",
        dest =          "exploration_steps",
        type =          int,
        default =       0,
        help =          """Number of steps for which agent should focus on exploring before acting 
                        from policy. Defaults to 0."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
    # Register commands.
    AGENT_COMMAND_REGISTRY.register_parsers(subparser = _subparser_)