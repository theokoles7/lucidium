"""# lucidium.spaces.base

Defines the abstract class representation for action and observation spaces.
"""

__all__ = ["Space"]

from abc            import ABC, abstractmethod
from typing         import Any, Optional, Sequence, Tuple, Union

from numpy          import dtype
from numpy.random   import seed
from numpy.typing   import DTypeLike, NDArray

class Space(ABC):
    """# Abstract Space

    Defines the abstract interface for an action or observation space.
    
    Adapted from: https://gymnasium.farama.org/_modules/gymnasium/spaces/space/#Space
    """
    
    def __init__(self,
        shape:          Optional[Sequence[int]] =   None,
        data_type:      Optional[DTypeLike] =       None,
        random_seed:    Optional[int] =             None
    ):
        """# Instantiate :class:`Space`.

        ## Args:
            * shape         (Sequence[int]):    Shape of :class:`Space`. Defaults to None for scalar.
            * data_type     (DTypeLike):        Data type of :class:`Space` elements.
            * random_seed   (int):              Value with which generator will be seeded.
        """
        # Define properties.
        self._shape_:   Optional[Tuple[int, ...]] = None if shape       is None else tuple(shape)
        self._dtype_:   Optional[DTypeLike] =       None if data_type   is None else dtype(data_type)
        
        # Seed space.
        self._seed_space_(random_seed = random_seed)
    
    # PROPERTIES ===================================================================================
    
    @property
    def dtype(self) -> DTypeLike:
        """# :class:`Space` Element Data Type."""
        return self._dtype_
    
    @property
    def is_continuous(self) -> bool:
        """# :class:`Space` is Continuous?"""
        return False
    
    @property
    def is_discrete(self) -> bool:
        """# :class:`Space` is Discrete?"""
        return False
    
    @property
    def is_flattenable(self) -> bool:
        """# :class:`Space` can be Flattened?"""
        return False
    
    @property
    def lower_bound(self) -> Optional[Union[float, NDArray]]:
        """# Lower Bound of :class:`Space` Elements."""
        return None
    
    @property
    def n(self) -> Optional[int]:
        """# :class:`Space` Discrete Size."""
        return None
    
    @property
    def shape(self) -> Optional[Tuple[int, ...]]:
        """# Shape of :class:`Space`."""
        return self._shape_
    
    @property
    def upper_bound(self) -> Optional[Union[float, NDArray]]:
        """# Upper Bound of :class:`Space` Elements."""
        return None
    
    # METHODS ======================================================================================
    
    @abstractmethod
    def contains(self,
        value:  Any
    ) -> bool:
        """# :class:`Space` Contains Value?
        
        ## Args:
            * value (Any):  Value being verified.

        True if value is an element of space.
        """
        pass
    
    @abstractmethod
    def sample(self) -> Any:
        """# Sample :class:`Space`.

        Randomly sample a valid element from space.
        """
        pass
    
    # HELPERS ======================================================================================
    
    def _seed_space_(self,
        random_seed:    Optional[int] =   None
    ) -> None:
        """# Seed :class:`Space`.

        ## Args:
            * seed  (int | Generator):  Random seed/generator.
        """
        if seed is not None: seed(random_seed)
    
    # DUNDERS ======================================================================================
    
    def __contains__(self,
        x:  Any
    ) -> bool:
        """# :class:`Space` Contains X?"""
        return self.contains(value = x)
    
    @abstractmethod
    def __repr__(self) -> str:
        """# :class:`Space` Object Representation.

        Object representation of space.
        """
        pass