"""# lucidium.symbolic.structure.composition.engine

This module provides the engine for symbolic composition:
- CompositionEngine:   Core engine for symbolic composition of predicates into patterns
"""

from collections                    import Counter
from re                             import findall
from typing                         import Any, Dict, List

from symbolic.logic.primitives      import Experience, Predicate
from symbolic.structure.patterns    import Pattern, PatternDiscoverer

class CompositionEngine():
    """# Composition Engine

    Core engine for symbolic composition of predicates into patterns.
    
    Mathematical foundation: Combinatorial optimization and symbolic reasoning.
    The engine composes predicates into meaningful patterns based on:
        1. Structural relationships (e.g., hierarchical composition)
        2. Semantic relationships (e.g., predicate compatibility)
    
    This implements a simplified version of symbolic composition focused on the specific 
    requirements of hierarchical predicate discovery.
    """
    
    def __init__(self,
        minimum_support:    int =   3,
        minimum_confidence: float = 0.7
    ):
        """# Instantiate Composition Engine.

        ## Args:
            * minimum_support       (int, optional):    Minimum support threshold for frequent 
                                                        patterns. Defaults to 3.
            * minimum_confidence    (float, optional):  Minimum confidence threshold for successful 
                                                        patterns. Defaults to 0.7.
        """
        # Initialize list of discovered predicates.
        self._discovered_predicates_:   List[Predicate] =   []
        
        # Initialize subsystems.
        self._pattern_discoverer_:      PatternDiscoverer = PatternDiscoverer(
                                                                minimum_support    =    minimum_support,
                                                                minimum_confidence =    minimum_confidence
                                                            )
        
    # PROPERTIES ===================================================================================
    
    @property
    def discovered_predicates(self) -> List[Predicate]:
        """# Discovered Predicates (List[Predicate])
        
        Returns the list of predicates discovered by the composition engine.
        """
        return self._discovered_predicates_
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """# Statistics (Dict[str, Any])
        
        Returns statistics about the composition engine's performance.
        
        ## Returns:
            * Dict[str, Any]: Dictionary containing statistics such as:
                - Number of discovered predicates
                - Pattern discovery parameters (support, confidence)
        """
        return  {
                    "total_discovered_predicates":  len(self._discovered_predicates_),
                    "average_confidence":           sum(
                                                        predicate.confidence 
                                                            for predicate
                                                            in self._discovered_predicates_
                                                    ) / len(self._discovered_predicates_) 
                                                            if self._discovered_predicates_
                                                            else 0.0,
                    "predicates":                   [
                                                        str(predicate)
                                                            for predicate
                                                            in self._discovered_predicates_
                                                    ],
                }
    
    # METHODS ======================================================================================
    
    def discover_and_create(self,
        experiences:    List[Experience]
    ) -> List[Predicate]:
        """# Discover and Create (Patterns).
        
        Discover meaningful patterns from experiences and create corresponding predicates.

        ## Args:
            * experiences   (List[Experience]): List of experiences to analyze for pattern discovery.

        ## Returns:
            * List[Predicate]:  List of discovered predicates representing meaningful patterns.
        """
        # Discover meaninfgul patterns.
        patterns:       List[Pattern] =     self._pattern_discoverer_.discover_patterns(
                                                experiences = experiences
                                            )
        
        # Initialize list of new discovered predicates from validated patterns.
        new_predicates: List[Predicate] =   []
        
        # For each pattern...
        for pattern in patterns:
            
            # If the pattern meets the criteria for predicate creation...
            if self._should_create_predicate_(
                patter =    pattern
            ):
                
                # Create a composite predicate from the pattern.
                composite_predicate:    Predicate = self._create_composite_predicate_(pattern)
                
                # Add the new predicate to the list.
                new_predicates.append(composite_predicate)
                
                # Add the new predicate to the discovered predicates.
                self._discovered_predicates_.append(composite_predicate)
                
        # Return the list of newly discovered predicates.
        return new_predicates
            
    # HELPERS ======================================================================================
    
    def _create_composite_predicate_(self,
        pattern:    Pattern
    ) -> Predicate:
        """# Create Composite Predicate
        
        Convert a validated pattern into a composite predicate.
        
        ## Args:
            * pattern   (Pattern):  The pattern to convert into a predicate.

        ## Returns:
            * Predicate:   The newly created composite predicate based on the pattern.
        """
        # Extract variables that unify across components.
        unified_variables:  List[str] = self._extract_unified_variables_(
                                            components =    pattern.components
                                        )
        
        # Create the composite predicate from the pattern.
        return  Predicate(
                    name =          pattern.name,
                    arguments =     tuple(unified_variables),
                    confidence =    pattern.confidence
                )
        
    def _extract_unified_variables_(self,
        components: List[str]
    ) -> List[str]:
        """# Extract Unified Variables
        
        Extract variables that unify across all components of a pattern.
        
        ## Args:
            * components   (List[str]):    List of predicate components to analyze.

        ## Returns:
            * List[str]:   List of unified variable names extracted from the components.
        """
        # Count variable occurrences across components
        variable_counts:    Counter =   Counter()
        
        # For each component in the pattern...
        for component in components:
            
            # Find all ?variable patterns.
            variables:      List[Any] = findall(r'\?(\w+)', component)
            
            # For each variable found, increment its count.
            for var in variables: variable_counts[var] += 1
        
        # Prefer variables that appear in multiple components
        unified_variabless: List[str] = [
                                            variable 
                                            for variable, count
                                            in variable_counts.items()
                                            if count > 1
                                        ]
        
        # If no cross-component variables...
        if not unified_variabless:  unified_variabless: List[str] = [
                                                                        variable
                                                                        for variable, _\
                                                                        in variable_counts.most_common(2)
                                                                    ]
        
          # Limit arity for practical use.
        return unified_variabless[:3]
    
    def _should_create_predicate_(self,
        pattern:    Pattern
    ) -> bool:
        """# Should Create Predicate?
        
        Determine if a pattern should be converted into a predicate based on its support and 
        confidence.
        
        ## Criteria:
            - Meets support threshold (frequency)
            - Meets confidence threshold (success correlation)
            - Not redundant with existing predicates

        ## Args:
            * pattern   (Pattern):  The pattern to evaluate.

        ## Returns:
            * bool: True if the pattern meets the criteria for predicate creation, False otherwise.
        """
        # If support is below threshold, skip.
        if pattern.support < self._pattern_discoverer_.minimum_support:                         return False
        
        # If confidence is below threshold, skip.
        if pattern.successes / pattern.support < self._pattern_discoverer_.minimum_confidence:  return False
        
        # Check for redundancy with existing predicates.
        return  all(
                    not pattern.name in {
                        predicate.name
                            for predicate
                            in self._discovered_predicates_
                    }
                )