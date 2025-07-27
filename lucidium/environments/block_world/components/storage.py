"""# lucidium.environments.block_world.components.storage

Defines the container for storing and reordering Blocks for the Block World environment.
"""

__all__ = ["BlockStorage"]

from typing                                             import Any, List, Optional

from lucidium.environments.block_world.components.block import Block

class BlockStorage():
    """# Block Storage

    Container class for storing all blocks in the Block World environment, with optional support for 
    randomized index ordering.

    Internally maintains:
    * A list of all `Block` instances.
    * An optional `random_order` permutation.
    * Index conversion helpers for order-aware access.
    """
    
    def __init__(self,
        blocks:         List[Block],
        random_order:   Optional[List[int]] =   None
    ):
        """# Instantiate Block Storage.

        ## Args:
            * blocks        (List[Block]):  List of all block instances to be stored.
            * random_order  (List[int]):    Index permutation for randomized block ordering.
        """
        # Define properties.
        self._blocks_:                  List[Block] =           blocks
        self._random_order_:            Optional[List[int]] =   random_order
        self._inverse_random_order_:    Optional[List[int]] =   None
        
        # Set random block order.
        self._set_random_order_()
        
    # PROPERTIES ===================================================================================
    
    @property
    def raw(self) -> List[Block]:
        """# Raw (Blocks)

        Original list of blocks in input order.
        """
        return self._blocks_.copy()
    
    @property
    def random_order(self) -> Optional[List[int]]:
        """# (Blocks') Random Order.

        Active random permutation (if any).
        """
        return self._random_order_
    
    # METHODS ======================================================================================
    
    def get_inverse_index(self,
        index:  int
    ) -> int:
        """# Get Inverse Index.
        
        Get the inverse permuted position of the index provided.

        ## Args:
            * index (int):  Index being converted to inverse permuted counterpart.

        ## Returns:
            * int:  Inverse permuted counterpart of index provided.
        """
        return index if self._inverse_random_order_ is None else self._inverse_random_order_[index]
    
    def get_random_index(self,
        index:  int
    ) -> int:
        """# Get Random Index.
        
        Get the permuted position of the index provided.

        ## Args:
            * index (int):  Index being converted to permuted counterpart.

        ## Returns:
            * int:  Permuted counterpart of index provided.
        """
        return index if self._random_order_ is None else self._random_order_[index]
    
    def permute(self,
        values: List[Any]
    ) -> List[Any]:
        """# Permute Values.

        ## Args:
            * values    (List[Any]):    Values being permuted.

        ## Raises:
            * ValueError:   If length of list does not match list of random ordered indices.

        ## Returns:
            * List[Any]:    Permuted list of values.
        """
        # If the length of the values does not match the number of blocks stored...
        if len(values) != len(self._blocks_):
            
            # Report error.
            raise   ValueError((
                        f"Permutation input length ({len(values)}) must match "
                        f"number of blocks stored ({len(self._blocks_)})."
                    ))
            
        # If no random order is defined, values cannot be permuted.
        if self._random_order_ is None: return values
        
        # Otherwise, provide permuted values.
        return [values[self._random_order_[i]] for i in range(len(self._blocks_))]
        
    # HELPERS ======================================================================================
    
    def _set_random_order_(self) -> None:
        """# Set Random Order.
        
        Set random order of blocks.
        
        ## Raises:
            * ValueError:   If length of permuted indices does not contain enough indices for each 
                            block in storage.
        """
        # If the random order is not defined, simply return.
        if self._random_order_ is None: return
        
        # If the random ordering does not consider all blocks stored...
        if len(self._random_order_) != len(self._blocks_):
            
            # Report error.
            raise   ValueError((
                        f"Length of permuted indices ({len(self._random_order_)}) "
                        f"must match length of blocks ({len(self._blocks_)})"
                    ))
            
        # Compute inverse random order.
        self._inverse_random_order_ =   sorted(
                                            range(len(self._random_order_)),
                                            key = lambda i: self._random_order_[i]
                                        )
        
    # DUNDERS ======================================================================================
    
    def __getitem__(self,
        index:  int
    ) -> Block:
        """# Get Block.

        ## Args:
            * index (int):  Index of block being accessed.

        ## Returns:
            * Block:    Block at index provided.
        """
        # If no random order is current defined...
        if self._random_order_ is None:
            
            # Then simply return block at index.
            return self._blocks_[index]
        
        # Otherwise, compute corresponding index in random order defined and return that block.
        return self._blocks_[self._random_order_[index]]
    
    def __len__(self) -> int:
        """# Block Quantity.

        ## Returns:
            * int:  Quantity of blocks currently stored.
        """
        return len(self._blocks_)
    
    def __repr__(self) -> str:
        """# (BlockStorage) Object Representation."""
        return f"""<BlockStorage(size = {len(self._blocks_)})>"""