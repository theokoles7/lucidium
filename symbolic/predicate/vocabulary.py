"""# lucidium.symbolic.predicates.PredicateVocabulary

Manage vocabulary of predicate signatures available to system.
"""

__all__ = ["PredicateVocabulary"]

from typing                         import Any, Dict, List, Optional, Set

from symbolic.predicate.__base__    import Predicate
from symbolic.predicate.category    import PredicateCategory
from symbolic.predicate.signature   import PredicateSignature


class PredicateVocabulary():
    """# Predicate Vocabulary.
    
    Manages the vocabulary of predicate signatures available to the system.
    
    This is the "dictionary" of all possible predicates the system can use, both basic 
    (hand-defined) and discovered (learned during training).
    """
    
    def __init__(self):
        """# Instantiate Predicate Volcabvulary
        
        Initialize vocabulary of predicate signatures.
        """
        # Initialize signatures dictionary.
        self._signatures_:  Dict[str, PredicateSignature] =     {}
        
        # Initialize categorized signature dictionary.
        self._by_category_: Dict[PredicateCategory, Set[str]] = {
                                                                    category:   set()
                                                                    for category
                                                                    in PredicateCategory
                                                                }
        
        # Initialize signature dictionary organized by arity.
        self._by_arity_:    Dict[int, Set[str]] =               {}
        
        # Initialize basic predicates.
        self._init_basic_predicates_()
        
    def __contains__(self,
        name:   str
    ) -> bool:
        """# Vocabulary Contains.
        
        Indicate the existence of a signature name in vocbulary.

        ## Args:
            * name  (str):  Signature name to search for in vocabulary.

        ## Returns:
            * bool:
                * True:     Name ∈ Vocabulary
                * False:    Name ∉ Vocabulary
        """
        return name in self._signatures_
    
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of vocabulary.

        ## Returns:
            * str:  Vocabulary string representation.
        """
        return f"""PredicateVocabulary({self.size} predicates)"""
        
    def _init_basic_predicates_(self):
        """# Initialize Basic Predicates.
        
        Initialize the vocabulary with fundamental predicates.
        """
        # For each fundamental signature being defined...
        for signature in [
            
            # Attribute signatures =================================================================
            
            # Color.
            PredicateSignature(
                name =          "color",
                arg_types =     ["object", "color_value"],
                category =      PredicateCategory.ATTRIBUTE,
                description =   "Object is of specified color."
            ),
            
            # Shape.
            PredicateSignature(
                name =          "shape",
                arg_types =     ["object", "shape_value"],
                category =      PredicateCategory.ATTRIBUTE,
                description =   "Object is of specified shape."
            ),
            
            # Size.
            PredicateSignature(
                name =          "size",
                arg_types =     ["object", "size_value"],
                category =      PredicateCategory.ATTRIBUTE,
                description =   "Object is of specified size."
            ),
            
            # Type.
            PredicateSignature(
                name =          "type",
                arg_types =     ["object", "type_value"],
                category =      PredicateCategory.ATTRIBUTE,
                description =   "Object is of specified type."
            ),
            
            # Functional signatures ================================================================
            
            # Movable.
            PredicateSignature(
                name =          "movable",
                arg_types =     ["object"],
                category =      PredicateCategory.FUNCTIONAL,
                description =   "Object can be moved."
            ),
            
            # Openable.
            PredicateSignature(
                name =          "openable",
                arg_types =     ["object"],
                category =      PredicateCategory.FUNCTIONAL,
                description =   "Object can be opened."
            ),
            
            # Locked.
            PredicateSignature(
                name =          "locked",
                arg_types =     ["object"],
                category =      PredicateCategory.FUNCTIONAL,
                description =   "Object is locked."
            ),
            
            # Spatial signatures ===================================================================
            
            # Near.
            PredicateSignature(
                name =          "near",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is close to object 2."
            ),
            
            # Above.
            PredicateSignature(
                name =          "above",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is above object 2."
            ),
            
            # Under.
            PredicateSignature(
                name =          "under",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is under object 2."
            ),
            
            # On.
            PredicateSignature(
                name =          "on",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is on top of object 2."
            ),
            
            # Left of.
            PredicateSignature(
                name =          "left_of",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is left of object 2."
            ),
            
            # Right of.
            PredicateSignature(
                name =          "right_of",
                arg_types =     ["object1", "object2"],
                category =      PredicateCategory.SPATIAL,
                description =   "Object 1 is right of object 2."
            ),
            
            # Temporal signatures ==================================================================
            
            # Before.
            PredicateSignature(
                name =          "before",
                arg_types =     ["event1", "event2"],
                category =      PredicateCategory.TEMPORAL,
                description =   "Event 1 occurs before event 2."
            ),
            
            # After.
            PredicateSignature(
                name =          "after",
                arg_types =     ["event1", "event2"],
                category =      PredicateCategory.TEMPORAL,
                description =   "Event 1 occurs after event 2."
            ),
        ]:
            # Add signature to vocabulary.
            self.add_signature(signature = signature)
            
    def add_signature(self,
        signature:  PredicateSignature
    ) -> bool:
        """# Add Signature.
        
        Add a signature to the vocabulary if it does not already exist. NOTE: Determination of the 
        prior existence of the signature strictly depends on the name of the signature.

        ## Args:
            * signature (PredicateSignature):   Signature being added.

        ## Returns:
            * bool: 
                * True:     Signatue successfully added to vocabulary.
                * False:    Signature name already exists.
        """
        # Return False if signature name already exists in vocabulary.
        if signature.name in self._signatures_: return False
        
        # Add signature to vocbulary.
        self._signatures_[signature.name] = signature
        
        # Add signature to category index.
        self._by_category_[signature.category].add(signature.name)
        
        # If signature's arity is not already accounted for in arity index...
        if signature.arity not in self._by_arity_:
            
            # Initialize index for that arity.
            self._by_arity_[signature.arity] =  set()
            
        # Add signature to arity index.
        self._by_arity_[signature.arity].add(signature.name)
        
        # Indicate successful signature registration.
        return True
    
    def create_predicate(self,
        name:       str,
        arguments:  List[Any],
        confidence: float =     1.0
    ) -> Optional[Predicate]:
        """#  Create Predicate.

        ## Args:
            * name          (str):              Name of predicate being created.
            * arguments     (List[Any]):        Arguments with which predicate will be defined.
            * confidence    (float, optional):  Confidence in predicate. Defaults to 1.0.

        ## Returns:
            * Optional[Predicate]:  Predicate created if valid.
        """
        # If name does not already exists in vocabulary, return None.
        if name not in self._signatures_: return None
            
        # Otherwise, create Predicate.
        try:                return  Predicate(
                                        name =          name,
                                        arguments =     arguments,
                                        signature =     self.get_signature(name),
                                        confidence =    confidence
                                    )
        
        # Return None if Predicate parameters were invalid.
        except ValueError:  return  None
    
    def get_by_arity(self,
        arity:   int
    ) -> List[PredicateSignature]:
        """# Get Signatures of Arity.
        
        Get all signatures in vocabulary that possess given arity.

        ## Args:
            * arity (int):  Predicate arity list being fetched.

        ## Returns:
            * List[PredicateSignature]: List of predicate signatures of given arity.
        """
        return  [
                    self._by_arity__[name]
                    for name
                    in self._by_arity_.get(arity, set())
                ]
    
    def get_by_category(self,
        category:   PredicateCategory
    ) -> List[PredicateSignature]:
        """# Get Signatures in Category.
        
        Get all signatures in vocabulary that pertain to the given category.

        ## Args:
            * category  (PredicateCategory):    Predicate category list being fetched.

        ## Returns:
            * List[PredicateSignature]: List of predicate signatures of given category.
        """
        return  [
                    self._signatures_[name]
                    for name
                    in self._by_category_.get(category, set())
                ]
            
    def get_signature(self,
        name:   str
    ) -> PredicateSignature:
        """# Get Signature.
        
        Fetch signature from vocabular by name.

        ## Args:
            * name  (str):  Name of signature being fetched.

        ## Returns:
            * PredicateSignature:   Predicate signature requested, if it exists.
        """
        return self._signatures_.get(key = name)
    
    def list_names(self) -> List[str]:
        """# List Names.
        
        Provide list of all signature names contained in vocabulary.

        ## Returns:
            * List[str]:    List of signature names.
        """
        return list(self._signatures_.keys())
    
    @property
    def size(self) -> int:
        """# Get Size.
        
        Provide the quantity of signatures in vocabulary.

        ## Returns:
            * int:  Number of signatures in vocbulary.
        """
        return len(self._signatures_)