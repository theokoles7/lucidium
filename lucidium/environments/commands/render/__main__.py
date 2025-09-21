"""# lucidium.environemnts.commands.render.main

Environment's rendering process.
"""

__all__ = ["main"]

from typing                                         import Any, Literal, Union

from lucidium.environments.__base__                 import Environment
from lucidium.environments.commands.render.__args__ import register_render_parser
from lucidium.registration                          import ENVIRONMENT_REGISTRY, register_environment_command

class Rendering():
    """# Rendering (Process)
    
    Process execution for rendering an environment.
    """
    
    def __init__(self,
        environment:    str,
        render_mode:    Literal["ansi", "ascii", "rgb"] =   "ansi",
        save_rendering: bool =                              False,
        save_path:      str =                               "output/renderings",
        **kwargs
    ):
        """# Instantiate Rendering Process.

        ## Args:
            * environment       (str):  Environment being rendered.
            * render_mode       (str):  Mode in which environment will be rendered ("ansi", "ascii", 
                                        or "rgb"). NOTE: Not all environments will necessarily 
                                        support every rendering mode. Defaults to "ansi".
            * save_rendering    (bool): If true, rendering will be saved to file. Defaults to False.
            * save_path         (str):  Path at which rendering will be saved. NOTE: Only applies if 
                                        "--save-rendering" or "--save" flags are passed. Defaults to 
                                        "output/renderings".
        """
        # Load environment rendering.
        _environment_:          Environment =   ENVIRONMENT_REGISTRY.load(name = environment, **kwargs)
        
        try:# Render environment.
            self._rendering_:   Union[str, Any] =   _environment_.render(render_mode = render_mode)
            
            # Provide rendering.
            print(self._rendering_)
            
        # Report that environment doesn't support provided rendering mode.
        except RuntimeError as e: print(e)
        

@register_environment_command(
    name =      "render",
    parser =    register_render_parser
)
def main(**kwargs) -> None:
    """# Render Environment."""
    # Execute rendering.
    Rendering(**kwargs)