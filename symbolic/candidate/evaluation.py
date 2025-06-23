"""# lucidium.symbolic.candidate.Evaluator

Evaluate composition candidates using statistical metrics.
"""

from re import findall
from typing import Any, Dict, List, Set

class Evaluator():
    """# (Candidate) Evaluator
    
    Calculates statistical metrics for evaluating composition candidates:
        - Confidence:       How reliable the pattern is
        - Utility:          How useful the pattern is for achieving goals  
        - Co-occurrence:    How often components appear together
        - Distinctiveness:  How unique/novel the pattern is
    """
    
    def __init__(self):
        """# Instantiate (Candidate) Evaluator."""
        # Initialize metrics.
        self._co_occurrence_:   float = 0.0
        self._distinctiveness_: float = 0.0
        self._utility_:         float = 0.0
        
        
    # PROPERTIES ===================================================================================
    
    @property
    def co_occurrence(self) -> float:
        """# Co-Occurrence.

        ## Returns:
            * float:    Co-occurrence metric.
        """
        return self._co_occurrence_
    
    @property
    def distinctiveness(self) -> float:
        """# Distinctiveness.

        ## Returns:
            * float:    Distinctiveness metric.
        """
        return self._distinctiveness_
    
    @property
    def utility(self) -> float:
        """# Utility.
        
        ## Returns:
            * float:    Utility metric.
        """
        return self._utility_
    
    
    # SETTERS ======================================================================================
    
    @co_occurrence.setter
    def co_occurrence(self,
        value:  float
    ) -> None:
        """# Co-Occurrence Setter.
        
        Value will be clamped between 0.0 and 1.0.

        ## Args:
            * value (float):    New co-occurrence value.
        """
        self._co_occurrence_ = max(0.0, min(value, 1.0))
        
    @distinctiveness.setter
    def distinctiveness(self,
        value:  float
    ) -> None:
        """# Distinctiveness Setter.
        
        Value will be clamped between 0.0 and 1.0.

        ## Args:
            * value (float):    New distinctiveness value.
        """
        self._distinctiveness_ = max(0.0, min(value, 1.0))
        
    @utility.setter
    def utility(self,
        value:  float
    ) -> None:
        """# Utility Setter.
        
        Value will be clamped between 0.0 and 1.0.

        ## Args:
            * value (float):    New utility value.
        """
        self._utility_ = max(0.0, min(value, 1.0))
        
    
    # METHODS ======================================================================================
    
    def calculate_binding_diversity(self,
        evidence_instances: List[Dict[str, Any]]
    ) -> float:
        """# Calculate Binding Diversity.
        
        Measures how many different variable binding combinations this pattern covers. Higher 
        diversity indicates a more generalizable pattern.
        
        Mathematical basis: Entropy of the binding distribution.
        
        ## Args:
            * evidence_instances    (List[Dict[str, Any]]): All evidence instances.
        
        ## Returns:
            * float:    Diversity score [0, 1].
        """
        # Calculation requires more than one instance of evidence.
        if len(evidence_instances) <= 1: return 0.0
        
        # Initialize set to store unique bindings.
        unique_bindings:    Set[str] =  set()
        
        # For each instance of evidence provided...
        for instance in evidence_instances:
            
            # Extract match bindings.
            bindings = instance.get("match", {}).get("bindings", {})
            
            # Create canonical string representation.
            binding_signature:  str =   "_".join(
                                            f"{k}:{v}"
                                            for k, v
                                            in sorted(bindings.items())
                                        )
            
            # Add binding to set.
            unique_bindings.add(binding_signature)
        
        # Diversity = unique_bindings / total_instances.
        return len(unique_bindings) / len(evidence_instances)
    
    def calculate_confidence(self,
        positive_evidence_count:    int,
        total_evidence_count:       int
    ) -> float:
        """# Calculate Confidence.
        
        Confidence score is based on positive vs negative evidence.
        Confidence = positive_instances / (positive_instances + negative_instances)

        ## Args:
            * positive_evidence_count   (int):  Count of positive evidence.
            * total_evidence_count      (int):  Count of evidence in total (positive + negative).

        ## Returns:
            * float:    Confidence score calculation, between 0.0 and 1.0.
        """
        return  0.0 if total_evidence_count == 0 \
                else (positive_evidence_count / total_evidence_count)
                
    def calculate_pattern_complexity(self,
        pattern_components:         List[str]
    ) -> float:
        """# Calculate Pattern Complexity.

        Args:
            * pattern_components    (List[str]):    Component patterns of candidate's pattern.

        ## Returns:
            * float:    Complexity calculation, between 0.0 and 1.0.
        """
        return  (
                    min(
                        1.0,
                        len(pattern_components) / 5.0
                    ) + 
                    min(
                        1.0,
                        len(set(
                            findall(r'\?(\w+)', component)
                            for component
                            in pattern_components
                        )) / 8.0)
                ) / 2.0
                
    def calculate_utility(self,
        positive_evidence_count:    int,
        total_evidence_count:       int,
    ) -> float:
        """# Calculate Utility.

        ## Args:
            * positive_evidence_count   (int):                              Count of positive 
                                                                            evidence.
            * total_evidence_count      (int):                              Count of evidence in 
                                                                            total (positive + 
                                                                            negative).
            * component_patterns        (List[str]):                        Component patterns of 
                                                                            candidate's pattern.
            * goal_achievement_data     (List[Dict[str, Any]], optional):   External episode data. 
                                                                            Defaults to None.

        ## Returns:
            * float:    Utility score calculation, between 0.0 and 1.0.
        """            
        # If there is no evidence data, utility is zero.
        if total_evidence_count == 0:   return 0.0
            
        # Otherwise, update utility from existing data.
        self._utility_: float = (
                                    positive_evidence_count / 
                                    total_evidence_count
                                )
        
        # Provide utility calculation.
        return self._utility_
        
                        
    # HELPERS ======================================================================================
    
    def _calculate_utility_from_external_data_(self,
        component_patterns: List[str],
        goal_achievement_data:  List[Dict[str, Any]]
    ) -> float:
        """# Calculate Utility from External Data.

        ## Args:
            * component_patterns    (List[str]):            Component patterns of candidate's pattern.
            * goal_achievement_data (List[Dict[str, Any]]): Episode data with outcomes.

        ## Returns:
            * float:    Utility score calculation, between 0.0 and 1.0.
        """
        # If no data was provided, utility is zero.
        if not goal_achievement_data: return 0.0
        
        # Initialize metric counts.
        relevant_episodes:              int =   0
        successful_with_composition:    int =   0
        
        # For each episode in data...
        for episode in goal_achievement_data:
            
            # If pattern was relevant to episode...
            if self._composition_relevant_to_episode_(
                component_patterns =    component_patterns,
                episode =               episode
            ):
                # Increment relevant episode count.
                relevant_episodes += 1
                
                # If episode was successful...
                if episode.get("success", False):
                    
                    # Increment success count.
                    successful_with_composition += 1
                    
        # If there were no relevant episodes, utility is zero.
        if relevant_episodes == 0:      return 0.0
        
        # Otherise, update utility.
        self._utility_ =    successful_with_composition / relevant_episodes
        
        # Provide utility calculation.
        return self._utility_
            
    def _composition_relevant_to_episode_(self,
        component_patterns: List[str],
        episode:            Dict[str, Any]
    ) -> bool:
        """# Is Composition Relevant to Episode?

        ## Args:
            * component_patterns    (List[str]):            Component patterns of candidate's pattern.
            * goal_achievement_data (List[Dict[str, Any]]): Episode data with outcome.

        ## Returns:
            * bool: True if composition is relevant to episode.
        """        
        # Simple heuristic: pattern is relevant if we have sufficient predicates and actions
        return  len(episode.get("predicates", []))  >=  len(component_patterns) \
            and len(episode.get("actions", []))     >   0