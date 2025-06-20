"""# lucidium.symbolic.composition.Candidate

Define structure and functionality of patter element candidate.
"""

from typing                         import Any, Dict, List

from symbolic.composition.pattern   import Pattern
from symbolic.logic.expressions     import Expression

class Candidate():
    """# Candidate.
    
    A candidate composition discovered from experience data.
    
    This class tracks the statistical evidence for a potential new composite predicate. As the agent 
    gains experience, it collects evidence for and against various composition patterns. When enough 
    evidence accumulates and meets the statistical criteria, the candidate can be promoted to an 
    actual composite predicate.
    
    ## Evidence collection process:
        1. Observe predicate co-occurrences in successful episodes
        2. Track when the pattern holds vs when it doesn't
        3. Calculate confidence, support, and utility metrics
        4. Decide whether to create the new composite predicate
        
    ## Properties:
        * pattern               (Pattern):              The composition pattern this candidate 
                                                        represents.
        * definition            (Expression):           Formal logical definition of the 
                                                        composition.
        * evidence_count        (int):                  Total number of evidence instances observed.
        * positive_instances    (List[Dict[str, Any]]): Cases where the pattern held and was useful.
        * negative_instances    (List[Dict[str, Any]]): Cases where the pattern failed or was 
                                                        misleading.
        * co_occurrence         (float):                How often component predicates appear 
                                                        together.
        * distinctiveness       (float):                How unique/distinguishing this pattern is.
        * utility               (float):                How useful this composition is for achieving 
                                                        goals.
    """
    
    def __init__(self,
        pattern:    Pattern,
        definition: Expression
    ):
        """# Instantiate Candidate.

        ## Args:
            * pattern       (Pattern):      The composition pattern this candidate represents.
            * definition    (Expression):   Formal logical definition of the composition.
        """
        # Define properties.
        self._pattern_:             Pattern =               pattern
        self._definition_:          Expression =            definition
        self._evidence_count_:      int =                   0
        self._positive_instances_:  List[Dict[str, Any]] =  []
        self._negative_instances_:  List[Dict[str, Any]] =  []
        
        # Initialize metrics.
        self._co_occurrence_:       float =                 0.0
        self._distinctiveness_:     float =                 0.0
        self._utility_:             float =                 0.0
        
    def _calculate_utility_from_external_data_(self,
        goal_achievement_data:  List[Dict[str, Any]]
    ) -> float:
        """# Calculate Utility from External Data.
    
        Original algorithm that searches external episode data for pattern relevance.

        ## Args:
            * goal_achievement_data (List[Dict[str, Any]]): List of episode data with outcomes.

        ## Returns:
            * float:    Utility score between 0.0 and 1.0.
        """
        # If there is no data provided, utility cannot be calculated.
        if not goal_achievement_data: return 0.0
    
        # Initialize counts.
        relevant_episodes:              int =   0
        successful_with_composition:    int =   0
        
        # For each episode in data...
        for episode in goal_achievement_data:
            
            # If composition was relevant to episode...
            if self._composition_relevant_to_episode_(episode):
                
                # Increment relevancy count.
                relevant_episodes +=                1
                
                # If episode was successful.
                if episode.get("success", False):
                    
                    # Increment success count.
                    successful_with_composition +=  1
        
        # If there were no relevant episodes, utility is zero.
        if relevant_episodes == 0: return 0.0
        
        # Calculate and update utility score.
        self._utility_:                 float = successful_with_composition / relevant_episodes
        
        return self._utility_
        
    def _composition_relevant_to_episode_(self,
        episode:    Dict[str, Any]
    ) -> bool:
        """# Composition Relevant to Episode?
        
        Check if this composition pattern was relevant to an episode.
        
        This is a simplified check - in practice, you'd want more sophisticated logic to determine 
        when a composition could have been applied.

        ##  Args:
            * episode   (Dict[str, Any]):   Episode data.

        ## Returns:
            * bool:
                * True:     Composition was relevant to episode.
                * False:    Composition was not relevant to episode.
        """
        # TODO: Implement sophisticated relevance checking. For now, this is just checking if 
        # component predicates appeared in episode.
        return len(episode.get("predicates", [])) > 0
        
    def add_negative_instance(self,
        instance:   Dict[str, Any]
    ) -> None:
        """# Add Negative Instance.
        
        Negative evidence comes from situations where:
            * The component predicates were true but the outcome was poor.
            * The composition would have led to incorrect decisions.
            * The pattern appeared spurious or misleading.

        ## Args:
            * instance  (Dict[str, Any]):   Dictionary containing the counter-evidence data.
        """
        # Append new instance.
        self.negative_instances.append(instance)
        
    def add_positive_instance(self,
        instance:   Dict[str, Any]
    ) -> None:
        """# Add Positive Instance.
        
        Positive evidence comes from situations where:
            * The component predicates were all true.
            * The resulting action/outcome was successful.
            * The composition would have been useful for decision-making.

        ## Args:
            * instance  (Dict[str, Any]):   Dictionary containing the evidence data, typically 
                                            including predicate bindings, context, and outcome 
                                            information.
        """
        # Append new instance.
        self.positive_instances.append(instance)
        
        # Increment evidence count.
        self.evidence_count += 1
        
    def calculate_utility(self,
        goal_achievement_data:  List[Dict[str, Any]] =  None
    ) -> float:
        """# Calculate Utility.

        ## Args:
            * goal_achievement_data (List[Dict[str, Any]]): List of episode data with outcomes.

        ## Returns:
            * float:    Utility score between 0.0 and 1.0.
        """
        # If external data provided...
        if goal_achievement_data is not None:
            
            # Use original algorithm.
            return  self._calculate_utility_from_external_data_(
                        goal_achievement_data = goal_achievement_data
                    )
    
        # Otherwise, use internal positive/negative instances
        total_instances:    int =   len(self.positive_instances) + len(self.negative_instances)
        
        # No evidence means no utility
        if total_instances == 0:    return 0.0
        
        # Update internal utility score
        self._utility_:     float = len(self.positive_instances) / total_instances
        
        # Provide calculation.
        return self._utility_
        
    @property
    def co_occurrence(self) -> float:
        """# Get Co-Occurence.

        ## Returns:
            * float:    How often component predicates appear together.
        """
        return self._co_occurrence_
    
    @co_occurrence.setter
    def co_occurrence(self,
        value:  float
    ) -> None:
        """# Set Co-Occurence.

        ## Args:
            * value (float):    Value to assign.
        """
        self._co_occurrence_ =  value
    
    @property
    def confidence(self) -> float:
        """# Get Confidence.
        
        Confidence score based on positive vs negative evidence.
        
        Confidence = positive_instances / (positive_instances + negative_instances)
        
        This measures how reliable the composition is - a high confidence means that when we see the 
        component predicates, the composition is usually valid and useful.

        ## Returns:
            * float:    Float between 0.0 and 1.0, where 1.0 means perfect confidence.
        """
        # Calculate total.
        total:  int =   len(self.positive_instances) + len(self.negative_instances)
        
        # Provide confidence.
        return 0.0 if total == 0 else len(self.positive_instances) / total
    
    @property
    def definition(self) -> Expression:
        """# Get Definition.

        ## Returns:
            * Expression:   Formal logical definition of the composition.
        """
        return self._definition_
    
    @property
    def distinctiveness(self) -> float:
        """# Get Distinctiveness.

        ## Returns:
            * float:    How unique/distinguishing this pattern is.
        """
        return self._distinctiveness_
    
    @distinctiveness.setter
    def distinctiveness(self,
        value:  float
    ) -> None:
        """# Set Distinctiveness.

        ## Args:
            * value (float):    Value being assigned.
        """
        self._distinctiveness_ = value
    
    @property
    def evidence_count(self) -> int:
        """# Get Evidence Count.

        ## Returns:
            * int:  Total number of evidence instances observed.
        """
        return self._evidence_count_
    
    @evidence_count.setter
    def evidence_count(self,
        value:  int
    ) -> None:
        """# Set Evidence Count.

        ## Args:
            * value (int):  Value being assigned.
        """
        self._evidence_count_ = value
    
    @property
    def meets_criteria(self) -> bool:
        """# Meets Criteria?
        
        Check if this candidate meets the pattern criteria for promotion.
        
        A composition candidate is ready to become an actual composite predicate when it has 
        sufficient statistical support (enough instances) and confidence (reliable pattern).

        ## Returns:
            * bool:
                * True:     Candidate should be promoted to a composite predicate.
                * False:    Candidate does not meet criteria to be promoted.
        """
        return  (
                    self.support    >= self.pattern.minimum_support
                    and
                    self.confidence >= self.pattern.confidence_threshold
                )
    
    @property
    def negative_instances(self) -> List[Dict[str, Any]]:
        """# Get Negative Instances.

        ## Returns:
            * List[Dict[str, Any]]: Cases where the pattern failed or was misleading.
        """
        return self._negative_instances_
        
    @property
    def pattern(self) -> Pattern:
        """# Get Pattern.

        ## Returns:
            * Pattern:  The composition pattern this candidate represents.
        """
        return self._pattern_
    
    @property
    def positive_instances(self) -> List[Dict[str, Any]]:
        """# Get Positive Instances.

        ## Returns:
            * List[Dict[str, Any]]: Cases where the pattern held and was useful.
        """
        return self._positive_instances_
    
    @property
    def support(self) -> int:
        """# Get Support.
        
        Number of positive instances supporting this composition.
        
        This is a key metric in association rule mining - it represents how frequently we've 
        observed this pattern in successful scenarios. Higher support means more evidence 
        that this is a valid composition.

        ## Returns:
            * int:  Number of positive instances supporting this composition.
        """
        return len(self.positive_instances)
    
    @property
    def utility(self) -> float:
        """# Get Utility Score.

        ## Returns:
            * float:    How useful this composition is for achieving goals.
        """
        return self._utility_