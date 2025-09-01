"""# lucidium.memory.replay.utilities.sum_tree

Sum tree implementation for prioritized experience replay policy.
"""

__all__ = ["SumTree"]

from numpy          import float32, full, inf, zeros
from numpy.typing   import NDArray

class SumTree():
    """# :class:`SumTree`
    
    Internal data structure for Prioritized Experience Replay.

    A sum-tree is a complete binary tree stored in array form where:
    * Leaves:           (the last `capacity` nodes) store per-transition priorities p_i.
    * Internal nodes:   Store the sum of their children (for proportional sampling) and the min of 
                        their children (for computing normalization constants).

    This allows:
    * O(log N) updates:     When a leaf's priority changes, update ancestors.
    * O(log N) sampling:    Given a prefix-sum mass, descend the tree to find the corresponding index.
    
    ## Notes:
    * The tree capacity is padded to the next power-of-two for simplicity.
    * The API is intentionally minimal — sufficient for PER.
    """
    
    def __init__(self,
        capacity:   int
    ):
        """# Instantiate Sum Tree.

        ## Args:
            * capacity  (int):  Maximum number of leaf nodes, corresponding to the maximum capacity 
                                of the buffer represented by the tree.
        """
        # Ensure that capacity is positive.
        if capacity <= 0: raise ValueError(f"Capacity expected to be positive integer, got {capacity}")
        
        # Initialize count.
        self._n_:       int =   1
        
        # n = power-of-two envelope size >= capacity.
        while self._n_ < capacity: self._n_ <<= 1
        
        # Define size.
        self._size_:    int =   capacity
        
        # Initialize sum tree.
        self._sum_tree_:    NDArray =   zeros(2 * self._n_, dtype = float32)
        
        # Initialize minimum tree.
        self._min_tree_:    NDArray =   full(2 * self._n_, fill_value = inf, dtype = float32)
        
    # PROPERTIES ===================================================================================
    
    @property
    def minimum(self) -> float:
        """# Tree Minimum

        Minimum priority among all leaves.
        """
        return float(self._min_tree_[1])
    
    @property
    def total(self) -> float:
        """# Tree Total

        Sum of all priorities.
        """
        return float(self._sum_tree_[1])
        
    # METHODS ======================================================================================
    
    def find_prefix_sum_index(self,
        mass:   float
    ) -> int:
        """# Find Prefic Sum Index.

        ## Args:
            * :param:`mass` (float):    Cumulative priority mass to locate, in [0, `total()`].

        ## Returns:
            * int:  Index in [0, `capacity`) of the sampled leaf.
        """
        # Start at root.
        index:  int =   1
        
        # Until leaf is reached...
        while index < self._n_:
            
            # Compute left node index.
            left:   int =   2 * index
            
            # Go left if cumulative mass is still within left child.
            if self._sum_tree_[left] >= mass: index = left
            
            # Otherwise...
            else:
                
                # Subtract left child's mass.
                mass -= self._sum_tree_[left]
                
                # And go right.
                index = left + 1
                
        # Provide the index.
        return index - self._n_
    
    def update(self,
        index:  int,
        value:  float
    ) -> None:
        """# Update Value.
        
        Set the priority value of leaf node `index`.
        
        This updates both the sum-tree and the minimum-tree in O(log N).

        ## Args:
            * :param:`index`    (int):      Leaf index in [0, `capacity`].
            * :param:`value`    (float):    New priority value (already adjusted by alpha).
        """
        # Convert to lead offset in the array.
        leaf_index: int =   index + self._n_
        
        # Assign priority value to both trees.
        self._sum_tree_[leaf_index] =   value
        self._min_tree_[leaf_index] =   value
        
        # Get leaf's parent index.
        leaf_index //= 2
        
        # Walking back up to the root node...
        while leaf_index >= 1:
            
            # Update parent sum.
            self._sum_tree_[leaf_index] =   self._sum_tree_[2 * leaf_index] + self._sum_tree_[2 * leaf_index + 1]
            
            # Update parent minimum.
            self._min_tree_[leaf_index] =   min(self._sum_tree_[2 * leaf_index], self._sum_tree_[2 * leaf_index + 1])
            
            # Walk to parent.
            leaf_index //= 2