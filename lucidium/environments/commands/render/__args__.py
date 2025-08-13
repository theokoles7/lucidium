"""# lucidium.environments.commands.render.args

Argument definitions and parsing for environment rednering process.
"""

__all__ = ["register_render_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_render_parser(
    parent_subpoarser:  _SubParsersAction
) -> None:
    """# Register Render Parser.
    
    Add parser for environment rendering.

    ## Args:
        * parent_subpoarser (_SubParsersAction): Parent's sub-parser object.
    """
    # Initialize parser.
    _parser_:   ArgumentParser =    parent_subpoarser.add_parser(
        name =          "render",
        help =          "Render environment visualization.",
        description =   """Visualize environment in various modes."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # RENDERING MODE ===============================================================================
    _mode_:     _ArgumentGroup =    _parser_.add_argument_group(title = "Rendering Mode")
    
    _mode_.add_argument(
        "--mode", "--format",
        dest =          "render_mode",
        type =          str,
        choices =       ["ansi", "ascii", "rgb"],
        default =       "ansi",
        help =          """Type of visualization. Defaults to "ansi"."""
    )
    
    # STORAGE ======================================================================================
    _storage_:  _ArgumentGroup =    _parser_.add_argument_group(title = "Storage")
    
    _storage_.add_argument(
        "--save-rendering", "--save",
        dest =          "save_rendering",
        action =        "store_true",
        default =       False,
        help =          """Save rendering to file."""
    )
    
    _storage_.add_argument(
        "--save-to", "--save-path",
        dest =          "save_path",
        type =          str,
        default =       "output/renderings",
        help =          """Path at which rendering will be saved. Defaults to "./output/renderings/"."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+