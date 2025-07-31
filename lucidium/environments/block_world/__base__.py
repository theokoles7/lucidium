"""# lucidium.environments.block_world.base

Block World environment implementation.
"""

from lucidium.environments.__base__ import Environment

class BlockWorld(Environment):
    """# Block World (Environment)
    
    BlockWorld is a classic AI planning domain where blocks can be stacked on top of each other or 
    placed on a table. The goal is to rearrange blocks from an initial configuration to achieve a 
    target configuration.
    
    Adapted from: https://github.com/google/neural-logic-machines/tree/master/scripts/blocksworld
    """
    
    def __init__(self,
        block_quantity: int =   3,
        random_order:   bool =  False,
        one_stack:      bool =  False,
        **kwargs
    ):
        """# Instantiate Block World Environment.

        ## Args:
            * blocks    (int, optional):    Number of blocks to place in environment. Defaults to 3.
        """
        