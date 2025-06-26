"""# lucidium.symbolic.structure.patterns.pattern.

Pattern representation for discovered predicate combinations.
"""

from typing import List

class Pattern():
    """# Pattern
    Discovered pattern representing a meaningful predicate combination.
    
    Mathematical foundation: Association rule mining where patterns represent frequent itemsets with 
    statistical significance measures.
    
    ## A pattern captures:
    - Components:   The predicate combination that co-occurs
    - Statistics:    How often it appears and leads to success
    - Identity:     Generated name for the potential composite predicate
    
    ## Example:
        Pattern(
            components=["near(?agent, ?obj)", "color(?obj, red)"],
            name="accessible_red_object",
            support=5,
            successes=4
        )
        → confidence = 4/5 = 0.8
    """
    
    def __init__(self,
        name:       str,
        components: List[str],
        support:    int =       0,
        successes:  int =       0
    ):
        """# Instantiate Pattern.

        ## Args:
            * name          (str):              Descriptive name for the pattern.
            * components    (List[str]):        List of predicate combinations that form the 
                                                pattern.
            * support       (int, optional):    Support count indicating how often the pattern 
                                                appears. Defaults to 0.
            * successes     (int, optional):    Success count indicating how often the pattern leads 
                                                to success. Defaults to 0.
        """
        # Define attributes.
        self._name_:        str =       name
        self._components_:  List[str] = components
        self._support_:     int =       support
        self._successes_:   int =       successes
        
    # PROPERTIES ===================================================================================
    
    @property
    def components(self) -> List[str]:
        """# Components (List[str])
        
        Returns the list of predicate combinations that form the pattern.
        """
        return self._components_
    
    @property
    def confidence(self) -> float:
        """# Confidence (float)
        
        Returns the confidence score of the pattern as the ratio of successes to support.
        
        Confidence = (successes / support)
        """
        # Calculate confidence.
        return (self.successes / self.support) if self.support > 0 else 0.0
    
    @property
    def name(self) -> str:
        """# Name (str)
        
        Returns the descriptive name of the pattern.
        """
        return self._name_
    
    @property
    def successes(self) -> int:
        """# Successes (int)
        
        Returns the success count indicating how often the pattern leads to success.
        """
        return self._successes_
    
    @property
    def support(self) -> int:
        """# Support (int)
        
        Returns the support count indicating how often the pattern appears.
        """
        return self._support_
    
    # DUNDERS ======================================================================================
    
    def __str__(self) -> str:
        """# String Representation.
        
        Returns a string representation of the pattern including its name, components, support, and 
        confidence.
        
        ## Returns:
            * str: String representation of the pattern.
        """
        return f"{self.name}: {self.components} (sup={self.support}, conf={self.confidence:.2f})"