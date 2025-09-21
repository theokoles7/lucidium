"""# lucidium.environments.cart_pole.arguments

Argument definitions and parsing for cart pole environment.
"""

__all__ = ["register_cart_pole_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_cart_pole_parser(
    subparser:  _SubParsersAction
) -> None:
    """# Register Cart Pole Argument Parser.

    ## Args:
        * subparser (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize parser.
    _parser_:           ArgumentParser =    subparser.add_parser(
        name =          "cart-pole",
        help =          "Gymnasium's CartPole environment.",
        description =   """A pole is attached by an un-actuated joint to a cart, which moves along a 
                        frictionless track. The pendulum is placed upright on the cart and the goal 
                        is to balance the pole by applying forces in the left and right direction on 
                        the cart.""",
        epilog =        """Wrapper for Gymnasium's CartPole environment, which corresponds to the 
                        cart-pole problem described in "Neuronlike adaptive elements that can solve 
                        difficult learning control problems"."""
    )
    
    # Define sub-parser for actions.
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        dest =          "cart_pole_action",
        description =   "Cart Pole environment commands."
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # UNIVERSAL GYMNASIUM ARGUMENTS ================================================================
    _gym_:              _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Universal Gymnasium Arguments",
        description =   """These arguments apply to all Gymnasium environments."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+