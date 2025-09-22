"""# lucidium.agents.commands.train.args

Argument definitions and parsing for agent training process.
"""

__all__ = ["register_train_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction

from lucidium.registration  import ENVIRONMENT_REGISTRY

def register_train_parser(
    subparser:  _SubParsersAction
) -> None:
    """# Register Train Parser.

    ## Args:
        * subparser (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize parser.
    _parser_:       ArgumentParser =    subparser.add_parser(
        name =          "train",
        help =          "Train agent on environment.",
        description =   """Initiate episodic agent training process."""
    )
    
    # Initialize sub-parser.
    _subparser_:    _SubParsersAction = _parser_.add_subparsers(
        dest =          "environment",
        help =          """Environment on which agent will be trained."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # TRAIN PARAMETERS =============================================================================
    _parameters_:   _ArgumentGroup =    _parser_.add_argument_group(title = "Training Parameters")
    
    _parameters_.add_argument(
        "--episodes",
        dest =          "episodes",
        type =          int,
        default =       1000,
        help =          """Number of episodes for which training will be conducted. Defaults to 
                        1000."""
    )
    
    _parameters_.add_argument(
        "--max-steps",
        dest =          "max_episode_steps",
        type =          int,
        default =       1000,
        help =          """Maximum number of steps allowed during each episode. Defaults to 
                        1,000."""
    )
    
    _parameters_.add_argument(
        "--evaluation-interval", "--eval-interval",
        dest =          "evaluation_interval",
        type =          int,
        default =       100,
        help =          """Interval at which agent will be evaluated. Defaults to 100."""
    )
    
    # ENVIRONMENT ==================================================================================
    _environment_:  _ArgumentGroup =    _parser_.add_argument_group(title = "Environment Rendering")
    
    _environment_.add_argument(
        "--render-mode",
        dest =          "render_mode",
        type =          str,
        choices =       ["human", "rgb_array", "ansi", None],
        default =       None,
        help =          """Mode by which environment will be rendered during training. Defaults to 
                        None (will not be rendered)."""
    )
    
    # RECORD KEEPING ===============================================================================
    _recording_:    _ArgumentGroup =    _parser_.add_argument_group(title = "Record Keeping")
    
    _recording_.add_argument(
        "--save-model",
        dest =          "save_model",
        action =        "store_true",
        default =       False,
        help =          """Save model on conclusion of training process. Defaults to False."""
    )
    
    _recording_.add_argument(
        "--save-config",
        dest =          "save_config",
        action =        "store_true",
        default =       False,
        help =          """Save agent & environment configurations on conclusion of training 
                        process. Defaults to False."""
    )
    
    _recording_.add_argument(
        "--save-results",
        dest =          "save_results",
        action =        "store_true",
        default =       False,
        help =          """Save training statistics on conclusion of training process. Defaults to 
                        False."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
    # Register environment parsers.
    ENVIRONMENT_REGISTRY.register_parsers(subparser = _subparser_)