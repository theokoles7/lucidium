"""# lucidium.spaces.discrete

Defines a discrete (integer-indexed) space.
"""

__all__ = ["Discrete"]

from random                     import randint
from typing                     import Optional, override

from numpy                      import all as np_all, any as np_any, arange, int8, int64, integer, \
                                        isclose, issubdtype, logical_and, ndarray, sum as np_sum, where
from numpy.random               import choice

from lucidium.spaces.__base__   import Space
from lucidium.spaces.core       import Mask

class Discrete(Space):
    """# Discrete (Space)

    Scalar-valued discrete space.
    """
    
    def __init__(self,
        n:              int,
        start:          Optional[int] = 0,
        random_seed:    Optional[int] =     None
    ):
        """# Instantiate :class:`DiscreteSpace`.

        ## Args:
            * n             (int):  Number of elements.
            * start         (int):  Smallest element of space. Defaults to 0.
            * random_seed   (int):  Value with which generator will be seeded.
        """
        # Define properties.
        self._n_:       int =   int64(n)
        self._start_:   int =   int64(start)
        
        # Validate parameters.
        self.__post_init__()
        
        # Seed space.
        self._seed_space_(random_seed = random_seed)
        
        # Initialize space.
        super(Discrete, self).__init__(shape = (), data_type = int64, random_seed = random_seed)
        
    def __post_init__(self) -> None:
        """# Validate parameters.
        
        ## Raises:
            * AssertionError:   If n is not a positive integer.
        """
        assert issubdtype(self._n_, integer),     f"n expected to be an integer, got {type(self._n_)}"
        assert self._n_ > 0,                      f"Discrete space must have positive number of elements, got n = {self._n_}"
        assert issubdtype(self._start_, integer), f"start expected to be an integer, got {type(self._start_)}"
        assert self.contains(x = self._start_),   f"start must be an element of space"
    
    # PROPERTIES ===================================================================================
    
    @property
    def is_discrete(self) -> bool:
        """# :class:`DiscreteSpace` is Discrete?"""
        return True
    
    @override
    @property
    def is_flattenable(self) -> bool:
        """# :class:`DiscreteSpace` can be Flattened?"""
        return True
    
    @override
    @property
    def n(self) -> int:
        """# :class:`DiscreteSpace` N

        Number of elements in space.
        """
        return self._n_
    
    @property
    def start(self) -> int:
        """# Starting Value of :class:`DiscreteSpace`."""
        return self._start_
        
    # METHODS ======================================================================================
    
    def contains(self,
        x:  int
    ) -> bool:
        """# :class:`DiscreteSpace` Contains?
        
        ## Args:
            * x (int):  Value being verified.

        ## Returns:
            * bool: True if x ∈ S.
        """
        return isinstance(x, int) and self._start_ <= x < (self._start_ + self._n_)
    
    def sample(self,
        mask:           Optional[Mask] =    None,
        probability:    Optional[Mask] =    None
    ) -> int:
        """# Sample :class:`DiscreteSpace`.

        ## Returns:
            * int:  Random element from space.
        """
        # Ensure that only one mask is provided.
        if (mask is not None) and (probability is not None):
            raise ValueError("Only one mask can be provided at a time.")
        
        # If selection mask is provided...
        if mask is not None:
            
            # Validate mask.
            self._validate_mask_(mask = mask)
            
            # If mask contained any allowed action...
            if np_any(mask):
                
                # Provide sample from start.
                return self._start_ + choice(where(mask)[0])
            
            # Otherwise, simply return start.
            return self._start_
        
        # If probability mask is provided...
        if probability is not None:
            
            # Validate mask.
            self._validate_probabilities_(mask = probability)
            
            # Provide sample from start.
            return self._start_ + choice(arange(self._n_), p = probability)
        
        return randint(self._start_, self._start_ + self._n_ - 1)
    
    # HELPERS ======================================================================================
    
    def _validate_mask_(self,
        mask:   Mask
    ) -> None:
        """# Validate Mask.
        
        Assert that mask shape matches space shape and that it's the proper data type.

        ## Args:
            * mask  (Mask): Mask being validated.
        """
        # Validate mask type.
        assert isinstance(mask, ndarray),   f"Mask must NDArray, got {type(mask)}"
        
        # Valid element type.
        assert mask.dtype == int8,          f"Mask elements must be binary (int8), got {mask.dtype}"
        
        # Validate shape.
        assert mask.shape == (self._n_,),   f"Mask shape must be the same as space; {mask.shape} != ({self._n_},)"
        
    def _validate_probabilities_(self,
        mask:   Mask
    ) -> None:
        """# Validate Probability Mask.
        
        Assert that probability values are valid.

        ## Args:
            * mask  (Mask): Mask being validated.
        """
        # Validate mask properties.
        self._validate_mask_(mask = mask)
        
        # Validate that values are between 0 and 1.
        assert np_all(logical_and(mask >= 0, mask <= 1)), f"Mask elements must be between 0 and 1."
        
        # Validate that sum is close to 1.
        assert isclose(np_sum(mask), 1),                  f"Sum of mask elements must be close to 1."
    
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other:  "Discrete"
    ) -> bool:
        """# :class:`DiscreteSpace`s are Equal?

        ## Args:
            * other (Discrete): :class:`DiscreteSpace` being compared.

        ## Returns:
            * bool: True is :class:`DiscreteSpace`s have the same `n` and `start`.
        """
        return  all([
                    isinstance(other, Discrete),
                    self._n_     == other.n,
                    self._start_ == other.start
                ])
    
    def __repr__(self) -> str:
        """# :class:`DiscreteSpace` Object Representation.

        Object representation of discrete space.
        """
        return f"<Discrete(n = {self.n})>"