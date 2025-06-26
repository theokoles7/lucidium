"""# lucidium.symbolic.structure.patterns.discovery

This module provides pattern discovery functionality for symbolic reasoning.
"""

from collections                    import Counter, defaultdict
from itertools                      import combinations
from re                             import match, Match
from typing                         import Dict, List, Tuple

from symbolic.logic.primitives      import Experience, Predicate
from symbolic.structure.patterns    import Pattern

class PatternDiscoverer():
    """# Pattern Discoverer
    
    Core algorithm for discovering meaningful predicate combinations.
    
    Mathematical foundation: Frequent itemset mining and association rule learning.
    The algorithm finds predicate combinations that:
        1. Appear frequently together (support threshold)
        2. Correlate with successful outcomes (confidence threshold)
    
    This implements a simplified version of the Apriori algorithm focused on the specific 
    requirements of hierarchical predicate discovery.
    """
    
    def __init__(self,
        minimum_support:    int =   3,
        minimum_confidence: float = 0.7
    ):
        """# Instantiate Pattern Discoverer.

        ## Args:
            * minimum_support       (int, optional):    Minimum support threshold for frequent 
                                                        patterns. Defaults to 3.
            * minimum_confidence    (float, optional):  Minimum confidence threshold for successful 
                                                        patterns. Defaults to 0.7.
        """
        # Define attributes.
        self._minimum_support_:     int =   minimum_support
        self._minimum_confidence_:  float = minimum_confidence
        
    # PROPERTIES ===================================================================================
    
    @property
    def minimum_confidence(self) -> float:
        """# Minimum Confidence (float)
        
        Returns the minimum confidence threshold for successful patterns.
        """
        return self._minimum_confidence_
    
    @property
    def minimum_support(self) -> int:
        """# Minimum Support (int)
        
        Returns the minimum support threshold for frequent patterns.
        """
        return self._minimum_support_
    
    # METHODS ======================================================================================
    
    def discover_patterns(self,
        experiences:    List[Experience]
    ) -> List[Pattern]:
        """# Discover Patterns.
        
        Analyzes a list of experiences to discover patterns that meet the support and confidence
        thresholds defined in the discoverer.
        
        ## Process:
            1. Extract all predicate combinations from experiences
            2. Count occurrences and success correlations
            3. Filter by support and confidence thresholds
            4. Return validated patterns ready for promotion

        ## Args:
            * experiences   (List[Experience]): List of experiences to analyze for pattern 
                                                discovery.

        ## Returns:
            * List[Pattern]:    List of discovered patterns that meet the support and confidence 
                                thresholds.
        """
        # Count occurrences of all patterns in the experiences.
        pattern_stats:  Dict[Tuple[str], Tuple[int, int]] = self._count_pattern_occurrences_(
                                                                experiences =   experiences
                                                            )
        
        # Initialize list to hold discovered patterns.
        patterns:       List[Pattern] =                     []
        
        # For each pattern key in the statistics...
        for pattern_key, (support, successes) in pattern_stats.items():
            
            # Generate the pattern name and components.
            components: List[str] = list(pattern_key)
            name:       str =       self._generate_pattern_name_(
                                        components =    components
                                    )
            
            # Add the pattern to the list.
            patterns.append(
                Pattern(
                    components =    components,
                    name =          name,
                    support =       support,
                    successes =     successes
                )
            )
        
        # Filter patterns by support and confidence thresholds.
        return  [
                    pattern
                        for pattern
                        in patterns
                    if      pattern.support     >= self.minimum_support
                        and pattern.confidence  >= self.minimum_confidence
                ]
        
    # HELPERS ======================================================================================
    
    def _count_pattern_occurrences_(self,
        experiences:    List[Experience]
    ) -> Dict[Tuple[str], Tuple[int, int]]:
        """# Count Pattern Occurrences.
        
        Counts how many times a specific pattern appears in the list of experiences.
        
        ## Args:
            * experiences   (List[Experience]): List of experiences to search for the pattern.

        ## Returns:
            * Dict[Tuple[str], Tuple[int, int]]:    Dictionary mapping pattern components to a tuple 
                                                    of (support, successes).
        """
        # Initialize pattern statistics.
        statistics: Dict[Tuple[str], List[int, int]] =  defaultdict(lambda: [0, 0])
        
        # For each experience provided...
        for experience in experiences:
            
            # Convert predicates to pattern strings.
            patterns:   List[str] = [
                                        self._predicate_to_pattern_(predicate)
                                        for predicate 
                                        in experience.predicates
                                    ]
            
            # For each possible combination size...
            for size in [2, 3]:
                
                # For each combination of the given size...
                for combination in combinations(patterns, size):
                    
                    # Convert to tuple for immutability.
                    pattern_key:    Tuple[str] =    tuple(sorted(combination))
                    
                    # Count the occurrence of this pattern.
                    statistics[pattern_key][0] += 1
                    
                    # If the experience was successful, increment success count.
                    if experience.success: statistics[pattern_key][1] += 1
                    
        # Return the statistics as a dictionary.
        return {key: (value[0], value[1]) for key, value in statistics.items()}
    
    def _generate_pattern_name_(self,
            components: List[str]
        ) -> str:
        """# Generate Pattern Name.
        
        Generates a descriptive name for a discovered pattern based on its components.

        Args:
            components (List[str]): List of predicate components that form the pattern.

        Returns:
            str: Descriptive name for the discovered pattern based on its components.
        """
        # Initialize list to hold predicate names.
        predicates: List[str] = []
        
        # For each component in the pattern...
        for component in components:
            
            # Extract the predicate name using regex.
            predicate_match:    Match[str] =    match(r'(\w+)\(', component)
            
            # If a match is found, append the predicate name.
            if predicate_match: predicates.append(predicate_match.group(1))
        
        # If no predicates were found, return a generic name.
        if not predicates:          return "discovered_pattern"
        
        # If only one predicate, return its name.
        if len(predicates) == 1:    return predicates[0]
        
        # If two predicates, return their names combined.
        if len(predicates) == 2:    return f"{predicates[0]}_{predicates[1]}"
        
        # If three or more predicates, return a complex name.
        else:                       return f"{'_'.join(predicates[:2])}_complex"
                
    def _predicate_to_pattern_(self,
        predicate:  Predicate
    ) -> str:
        """# Predicate to Patter.
        
        Converts a predicate into a string representation suitable for pattern discovery.

        ## Args:
            * predicate (Predicate):    Predicate to convert.

        ## Returns:
            * str:  String representation of the predicate for pattern discovery.
        """
        # Form arguments string.
        arguments:  str =   ",".join([
                                f"?{argument}" 
                                    if argument.replace("_", "").isalnum() 
                                    else argument 
                                for argument 
                                in predicate.arguments
                            ])
        
        # Return formatted string.
        return f"{predicate.name}({arguments})"