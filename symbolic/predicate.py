"""# lucidium.symbolic.predicate

Symbolic predicate definition, structure, and utilities.
"""

from typing import Any, Dict, Tuple

from torch  import tensor, Tensor

class Predicate():
    """# Predicate
    
    Symbolic representation of a grounded predicate.
    """
    
    def __init__(self,
        name:   str,
        *args:  Any
    ):
        """# Instantiate Predicate.

        ## Args:
            * name  (str):  Predicate name.
        """
        # Define properties.
        self._name_:    str =           name
        self._args_:    Tuple[Any] =    tuple(args)
        
    # PROPERTIES ===================================================================================
    
    @property
    def arity(self) -> int:
        """# (Predicate) Arity

        Number of arguments attrbuted to predicate.
        """
        return len(self._args_)
        
    # METHODS ======================================================================================
    
    def to_tensor(self,
        vocabulary: Dict[str, int]
    ) -> Tensor:
        """# (Predicate) to Tensor

        ## Args:
            * vocabulary    (Dict[str, int]):   Mapping of terms to their numeric value.

        ## Returns:
            * Tensor:   Tensor representation of predicate.
        """
        return tensor([vocabulary.get(str(arg), -1) for arg in (self._name_, *self._args_)])
    
    def to_tuple(self) -> Tuple[Any]:
        """# (Predicate) to Tuple

        Tuple representation of predicate.
        """
        return (self._name_, *self._args_)
    
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other: "Predicate"
    ) -> bool:
        """# Predicate Equality.

        ## Args:
            * other (Predicate):    Predicate being compared.

        ## Returns:
            * bool: True if predicates have the same name and arguments.
        """
        return isinstance(other, Predicate) and self.to_tuple() == other.to_tuple()
    
    def __repr__(self) -> str:
        """# Object Representation."""
        return f"""<Predicate(name = {self._name_}, arity = {self.arity})>"""
    
    def __str__(self) -> str:
        """# String Representation."""
        return f"""{self._name_}({",".join(map(str, self._args_))})"""