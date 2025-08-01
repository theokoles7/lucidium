"""# lucidium.environments.block_world.components.world

Defines the Block World container that manages all logical block relationships and actions.
"""

__all__ = ["World"]

from functools                                              import cached_property
from random                                                 import choice
from typing                                                 import Dict, List, Optional, Tuple

from torch                                                  import tensor, Tensor

from lucidium.environments.block_world.components.block     import Block

class World():
    """# (Block World) World

    Central logic container for a Block World environment instance. Manages relationships between 
    blocks and enforces movement rules.

    Blocks are arranged as trees rooted in a single ground block, and actions such as `move()` 
    manipulate the tree by reassigning parent-child links.
    
    Adapted from: https://github.com/google/neural-logic-machines/tree/master/scripts/blocksworld
    """
    
    def __init__(self,
        block_quantity: List[Block] =           3,
        random_order:   Optional[List[int]] =   None,
        one_stack:      bool =                  False,
        **kwargs
    ):
        """# Instantiate World.

        ## Args:
            * block_quantity    (int):          Number of blocks to place in environment. Defaults to 3.
            * random_order      (List[int]):    Index permutation for randomized ordering of blocks.
        """
        # Define block index.
        self._block_index_: List[int] = list(range(block_quantity))
        
        # Define size.
        self._size_:        int =       block_quantity
        
        # Define one-stack flag.
        self._one_stack_:   bool =      one_stack
        
        # If random order is provided...
        if random_order is not None:
            
            # If the random order does not account for each block in world...
            if len(random_order) != block_quantity:
                
                # Report error.
                raise ValueError(f"Random order length ({len(random_order)}) must match number of blocks ({block_quantity})")
            
            # Update block index to be random permutation.
            self._block_index_ = random_order
        
        # Generate blocks.
        self.reset()
        
    # PROPERTIES ===================================================================================
    
    @property
    def blocks(self) -> List[Block]:
        """# Blocks.

        Blocks currently stored in world.
        """
        return self._blocks_.copy()
    
    @property
    def size(self) -> int:
        """# Block Quantity

        Quantity of blocks in world.
        """
        return self._size_
    
    @property
    def stacks(self) -> List[List[Block]]:
        """# (Block) Stacks.

        Current stack(s) of blocks in world.
        """
        # Extract ground block.
        ground: Block = self._blocks_[0]
        
        # Define recursive child appender.
        def collect_chain(block: Block) -> List[Block]:
            """# Collect (Block) Chain.

            ## Args:
                * block (Block):    Block whose children will be added to stack.
                
            ## Returns:
                * List[Block]:  Block's child chain.
            """
            return [block] + [child for c in block.children for child in collect_chain(c)]
            
        # Append chain to list of stacks.
        return [collect_chain(block = root) for root in [block for block in ground.children]]
    
    # METHODS ======================================================================================
            
    def block_is_moveable(self,
        from_index: int,
        to_index:   int
    ) -> bool:
        """# Block is Moveable?

        ## Args:
            * from_index    (int):  Block to be picked up.
            * to_index      (int):  Block to be stacked onto.

        ## Returns:
            * bool: True if block in question is moveable and the other block is placeable.
        """
        return self._blocks_[from_index].is_moveable and self._blocks_[to_index].is_placeable
    
    def encode(self) -> Tensor:
        """# Encode World.

        ## Returns:
            * Tensor:   Tensor representation of world.
        """
        
    
    def move_block(self,
        from_index: int,
        to_index:   int
    ) -> Tuple[bool, Dict[str, str]]:
        """# Move Block.

        Move a block onto another, if the move is allowed.

        ## Args:
            * from_index    (int):  Block to be picked up.
            * to_index      (int):  Block to be stacked onto.

        ## Raises:
            * ValueError:   If the move is not valid (blocked by constraints).
            
        ## Returns:
            * bool:             True if move was made successfully.
            * Dict[str, str]:   Event string.
        """
        # As long as indices are not the same, and the move is valid...
        if from_index != to_index \
            and self.block_is_moveable(from_index = from_index, to_index = to_index):
                
            # Pick up block.
            self._blocks_[from_index].pick_up()
            
            # Place block at intended position.
            self._blocks_[from_index].place_on(block = self._blocks_[to_index])
            
            # Provide result.
            return True, {"event": f"placed block {from_index} on {to_index}"}
        
        # Otherwise, report failure.
        return False, {"event": "attempted invalid move"}
    
    def reset(self) -> None:
        """# Reset (World).
        
        Reset world to initial state.
        """
        # Initialize base block.
        self._blocks_:  List[Block] =   [Block(id = 0)]
        
        # Initialize list of leaves.
        leaves:         List[Block] =   [self._blocks_[0]]
        
        # For each block needing to be initialized.
        for b in range(1, self.size + 1):
            
            # Choose a random leaf block.
            other:  Block = choice(leaves)
            
            # Create a new block.
            this:   Block = Block(id = b)
            
            # Place this block on the other block.
            this.place_on(block = other)
            
            # If the other block is no longer placeable, or if we're creating only one stack...
            if self._one_stack_:
                
                # Remove the other block from leaves.
                leaves.remove(other)
                
            # Add new block to lists.
            self._blocks_.append(this)
            leaves.append(this)
            
    # HELPERS ======================================================================================
    
    def _get_ground_blocks_(self) -> Tensor:
        """# Get Ground Blocks.

        ## Returns:
            * Tensor:   Tensor representation of ground blocks.
        """
        return tensor([block.is_ground for block in self._blocks_])
    
    def _get_moveable_blocks_(self) -> Tensor:
        """# Get Moveable Blocks.

        ## Returns:
            * Tensor:   Tensor representation of moveable blocks.
        """
        return tensor([block.is_moveable for block in self._blocks_])
    
    def _get_placeable_blocks_(self) -> Tensor:
        """# Get Placeable Blocks.

        ## Returns:
            * Tensor:   Tensor representation of placeable blocks.
        """
        return tensor([block.is_placeable for block in self._blocks_])
        
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other:  "World"
    ) -> bool:
        """# (Worlds) Are Equal?"""
        # Indicate that blocks in each world are equal.
        return  all([
                    this_block == other_block 
                    for this_block, other_block 
                    in zip(self.blocks, other.blocks)
                ])
    
    def __repr__(self) -> str:
        """# (World) Object Representation."""
        return f"""<World(size = {self.size})>"""
    
    def __str__(self) -> str:
        """# (World) String Representation."""
        # Initialize row lines.
        world:  List[str] = []
        
        # For each possible block level...
        for level in reversed(range(self.size)):
            
            # Initialize rendering rows.
            top, middle = [], []
            
            # For each block stack...
            for stack in self.stacks:
                
                # If there is a block in the stack at the current level...
                if len(stack) > level:
                    
                    # Append the top of the block.
                    top.append("┏━━━┓")
                    
                    # Append the block ID.
                    middle.append(f"┃{stack[level].id:^3}┃")
                    
                # Otherwise...
                else:
                    
                    # Append empty spaces.
                    top.append("     ")
                    middle.append("     ")
                    
            # Write to line.
            world.extend([" ".join(top), " ".join(middle)])
            
        # Form platform.
        world.append("━" * (self.size * 5 + self.size - 1))
        
        # Return world string.
        return "\n".join(world)