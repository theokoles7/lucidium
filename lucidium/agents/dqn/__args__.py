"""# lucidium.agents.dqn.args

Argument definitions and parsing for DQN agent.
"""

__all__ = ["register_dqn_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction

from lucidium.registries    import AGENT_COMMAND_REGISTRY

def register_dqn_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register DQN Argument Parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    
    # Initialize parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "dqn",
        help =          "Deep Q-Network agent.",
        description =   """DQN is an off-policy, model-free, deep-rl algorithm""",
        epilog =        """Implementation of Deep Q-Network (DQN) agent based on "Playing Atari with 
                        Deep Reinforcement Learning" by Mnih et al. (2013). Link to paper: 
                        https://arxiv.org/pdf/1312.5602"""
    )
    
    # Initialize sub-parser.
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        dest =          "agent_action",
        help =          """Actino that agent will execute."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+

    # DISCOUNT ============================================================
    _discount_:     _ArgumentGroup =    _parser_.add_argument_group(title = "Discount (Gamma)")
    
    _discount_.add_argument(
        "--discount-rate", "--gamma",
        dest =      "discount_rate",
        type =      float,
        default =   0.99,
        help =      """Determines the importance of future rewards. A factor of 0 will make the 
                    agent "myopic" (or short-sighted) by only considering current rewards, while a 
                    factor approaching 1 will make it strive for a long-term high reward. Defaults 
                    to 0.99."""
    )
    
    # EXPLORATION =========================================================
    _exploration_:  _ArgumentGroup =    _parser_.add_argument_group(title = "Exploration (Epsilon)")
    
    _exploration_.add_argument(
        "--exploration-rate", "--epsilon",
        dest =      "exploration_rate",
        type =      float,
        default =   1.0,
        help =      """Probability that the agent will choose a random action, rather than selecting 
                    the action that is believed to be optimal based on its current knowledge (i.e., 
                    the action with the highest Q-value). Defaults to 1.0."""
    )
    
    _exploration_.add_argument(
        "--exploration-decay", "--epsilon-decay",
        dest =      "exploration_decay",
        type =      float,
        default =   0.99,
        help =      """Controls how quickly the exploration rate (ϵ) decreases over time. A decay 
                    factor less than 1 (e.g., 0.995) causes the exploration rate to gradually 
                    decrease, leading to more exploitation as the agent learns more about the 
                    environment. Defaults to 0.99."""
    )
    
    _exploration_.add_argument(
        "--exploration-min", "--epsilon-min",
        dest =      "exploration_min",
        type =      float,
        default =   0.1,
        help =      """Specifies the minimum exploration rate that the agent will reach after the 
                    exploration decay process. This ensures that the agent does not completely stop 
                    exploring and retains a small chance to explore randomly, even in later stages 
                    of training. Defaults to 0.1."""
    )
    
    # TARGET NETWORK ======================================================
    _target_network_: _ArgumentGroup =  _parser_.add_argument_group(title = "Target Network")
    
    _target_network_.add_argument(
        "--target-tau",
        dest =      "target_tau",
        type =      float,
        default =   2e-3,
        help =      """Soft update rate for the target network. A smaller value results in slower 
                    updates, which can stabilize training. Defaults to 0.002."""
    )
    
    _target_network_.add_argument(
        "--update-interval",
        dest =      "update_interval",
        type =      int,
        default =   4,
        help =      """Interval (in steps) at which the target network is updated. Defaults to 4."""
    )
    
    # OPTIMIZER ===========================================================
    _optimizer_:    _ArgumentGroup =    _parser_.add_argument_group(title = "Optimizer")
    
    _optimizer_.add_argument(
        "--learning-rate", "--lr",
        dest =          "learning_rate",
        type =          float,
        default =       1e-3,
        help =          """Optimizer learning rate."""
    )
    
    # EXPERIENCE REPLAY ===================================================
    _replay_buffer_: _ArgumentGroup =   _parser_.add_argument_group(title = "Experience Replay")
    
    _replay_buffer_.add_argument(
        "--replay-buffer-capacity",
        dest =      "replay_buffer_capacity",
        type =      int,
        default =   int(1e6),
        help =      """Maximum capacity of the experience replay buffer. Defaults to 1,000,000."""
    )
    
    _replay_buffer_.add_argument(
        "--buffer-batch-size",
        dest =      "buffer_batch_size",
        type =      int,
        default =   64,
        help =      """Size of the batch sampled from the experience replay buffer. Defaults to 
                    64."""
    )
    
    # SEEDING =============================================================
    _seeding_:      _ArgumentGroup =    _parser_.add_argument_group(title = "Seeding")
    
    _seeding_.add_argument(
        "--random-seed",
        dest =      "random_seed",
        type =      int,
        default =   42,
        help =      """Random seed for reproducibility. Defaults to 42."""
    )
    
    _seeding_.add_argument(
        "--to-device",
        dest =      "to_device",
        type =      str,
        choices =   ["cpu", "cuda"],
        default =   "cpu",
        help =      """Device on which to run the agent (e.g., 'cpu' or 'cuda'). Defaults to 
                    'cpu'."""
    )
    

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
    # Register commands.
    AGENT_COMMAND_REGISTRY.register_parsers(subparser = _subparser_)