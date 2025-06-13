"""# lucidium.symbolic.predicate.PredicateSet

Define collection interface for predicates.
"""

__all__ = ["PredicateSet"]

from typing                         import Dict, Iterable, List, Optional

from symbolic.predicate.__base__    import Predicate
from symbolic.predicate.signature   import PredicateSignature

class PredicateSet():
    """# Predicate Set.
    
    A collection of predicate instances with efficient lookup and manipulation.
    
    Used to represent the symbolic state of an environment or the knowledge base of an agent at a 
    particular time.
    """
    
    def __init__(self,
        predicates: Optional[List[Predicate]] = None
    ):
        """# Instantiate Predicate Set.

        ## Args:
            * predicates    (Optional[List[Predicate]], optional):  List of predicates with which 
                                                                    set will be initialized.
        """
        # Initialize predicate dictionary.
        self._predicates_:  Dict[str, Predicate] =  {}
        
        # Add predicates passed.
        for predicate in predicates: self.add(predicate)
        
    def __iter__(self) -> Iterable[Predicate]:
        """# Get Iterable.
        
        Provide iterable of predicates.

        ## Returns:
            * Iterable[Predicate]:  Predicate iterable.
        """
        return iter(self._predicates_.values())
        
    def __len__(self) -> int:
        """# Get Length.
        
        Get length of predicate set.

        ## Returns:
            * int:  Length of predicate set.
        """
        return self.size
    
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate set.

        ## Returns:
            * str:  String representation of predicate set.
        """
        return self.__str__()
    
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of predicate set.

        ## Returns:
            * str:  String representation of predicate set.
        """
        # If set is empty, return empty string representation.
        if self.is_empty: return f"""PredicateSet(empty)"""
        
        # Otherwise, initialize string with up to 5 predicates.
        predicates: List[str] = [str(predicate) for predicate in self._predicates_[:5]]
        
        # If there are more than 5 predicates in the set, simply append an ellipses for brevity.
        if self.size > 5: predicates.append("...")
        
        # Return predicate set string.
        return f"""PredicateSet({",".join(predicates)})"""
        
    def add(self,
        predicate:  Predicate
    ) -> bool:
        """# Add Predicate.
        
        Add predicate to set. If it already exists in the set, its confidence will be updated.

        ## Args:
            * predicate (Predicate):    Predicate being added to set.

        ## Returns:
            * bool:
                * True:     Predicate successfully added.
                * False:    Predicate already exists in set.
        """
        # Get predicate's hash key.
        hash_key:   str =   predicate.hash_key
        
        # If predicate's hash key is already in the set...
        if hash_key in self._predicates_:
            
            # If the existing predicate's confidence is lower than the one provided...
            if self._predicates_[hash_key].confidence < predicate.confidence:
                
                # Replace with new predicate.
                self._predicates_[hash_key] = predicate
                
            # Return False to simulate that "predicate already exists".
            return False
        
        # Otherwise, simply add predicate anyway.
        self._predicates_[hash_key] = predicate
        
        # Return True.
        return True
    
    def contains(self,
        predicate:  Predicate
    ) -> bool:
        """# Set Contains.

        ## Args:
            * predicate (Predicate):    Predicate being searched for in set.

        ## Returns:
            * bool:
                * True:     Predicate ∈ PredicateSet
                * False:    Predicate ∉ PredicateSet
        """
        return predicate.hash_key in self._predicates_
    
    def filter_by_confidence(self,
        minimum: float
    ) -> "PredicateSet":
        """# Filter by Confidence.
        
        Get new set of predicates that have confidence of at least `minimum`.

        ## Args:
            * minimum   (float):    Minimum confidence required for predicate.

        ## Returns:
            * PredicateSet: New predicate set in which each predicate has at least `minimum` 
                            confidence.
        """
        return  PredicateSet(
                    predicates =    [
                                        predicate
                                        for predicate
                                        in self._predicates_.values()
                                        if predicate.confidence >= minimum
                                    ]
                )
    
    def get_by_name(self,
        name:   str
    ) -> List[Predicate]:
        """# Get Predicates by Name.
        
        Get list of all predicates in set with matching name.

        ## Args:
            * name  (str):  Predicate name to search for in set.

        ## Returns:
            * List[Predicate]:  List of all predicates in set with matching name.
        """
        return  [
                    predicate
                    for predicate
                    in self._predicates_.values()
                    if predicate.name == name
                ]
    
    def get_by_signature(self,
        signature:  PredicateSignature
    ) -> List[Predicate]:
        """# Get Predicates by Signature.
        
        Get list of all predicates in set with matching signature.

        ## Args:
            * signature (PredicateSignature):   Predicate signature to search for in set.

        ## Returns:
            * List[Predicate]:  List of all predicates in set with matching signature.
        """
        return  [
                    predicate
                    for predicate
                    in self._predicates_.values()
                    if predicate.signature == signature
                ]
        
    def intersection(self,
        other:  "PredicateSet"
    ) -> "PredicateSet":
        """# Get Intersection.
        
        Produce intersection of two predicate sets.

        ## Args:
            * other (PredicateSet): Predicate set with which self will be intersected.

        ## Returns:
           * PredicateSet:  Intersection of self and other predicate sets.
        """
        # Initialize empty set.
        intersection:   PredicateSet =  PredicateSet()
        
        # For each predicate in set...
        for hash_key, predicate in self._predicates_.items():
            
            # If the hash key also exists in other set...
            if hash_key in other._predicates_:
                
                # Add predicate to intersection.
                intersection.add(predicate = predicate)
                
        # Return intersection.
        return intersection
    
    @property
    def is_empty(self) -> bool:
        """# Set is Empty.
        
        Indicate if set is empty or not.

        ## Returns:
            * bool:
                * True:     Set is empty.
                * False:    Set is not empty.
        """
        return len(self._predicates_) == 0
    
    def remove(self,
        predicate:  Predicate
    ) -> bool:
        """# Remove Predicate.
        
        Remove predicate from set.

        ## Args:
            * predicate (Predicate): Predicate being removed.

        ## Returns:
            * bool:
                * True:     Predicate successfully removed.
                * False:    Predicate is not in set.
        """
        # If the predicate's hash key exists...
        if predicate.hash_key in self._predicates_:
            
            # Delete the predicate.
            del self._predicates_[predicate.hash_key]
            
            # Indicate deletion.
            return True
        
        # Otherwise, indicate that predicate is not in set.
        return False
    
    @property
    def size(self) -> int:
        """# Get Size.
        
        Provide the size of the predicate set.

        ## Returns:
            * int:  Size of predicate set.
        """
        return len(self._predicates_)
    
    def to_list(self) -> List[Predicate]:
        """# Get Predicate List.
        
        Convert predicate set to list.

        ## Returns:
            * List[Predicate]:  List of predicates in set.
        """
        return list(self._predicates_.values())

    def union(self,
        other:  "PredicateSet"
    ) -> "PredicateSet":
        """# Get Union.
        
        Produce union of two predicate sets.

        ## Args:
            * other (PredicateSet): Predicate set that will be unioned with self.

        ## Returns:
            * PredicateSet: Union of self and other predicate sets.
        """
        # Create a copy of self.
        union:  PredicateSet =  PredicateSet(
                                    predicates =    self.to_list()
                                )
        
        # Add each predicate from other set.
        for predicate in other.to_list(): self.add(predicate = predicate)
        
        # Return union.
        return union