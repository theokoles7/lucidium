"""# lucidium.symbolic.composition.Candidate

Define structure and functionality of patter element candidate.
"""

from re                             import match, Match
from typing                         import Any, Dict, List, Optional

from symbolic.composition.pattern   import Pattern
from symbolic.logic                 import Expression
from symbolic.predicate             import Predicate, PredicateSet

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
        
    def _accessibility_pattern_actionable_(self,
        episode_predicates:     PredicateSet,
        episode_actions:        List[str]
    ) -> bool:
        """# Is Accessibility Pattern Actionable?
    
        Check if accessibility patterns are actionable in this episode.
        
        ## Accessibility is actionable if:
            1. There are movement/interaction actions
            2. There are objects that can be interacted with
            3. The episode involves achieving goals through object manipulation
        
        ## Args:
            * episode_predicates    (PredicateSet): Episode predicates.
            * episode_actions       (List[str]):    Actions taken.
        
        ## Returns:
            * bool: True if accessibility pattern was actionable.
        """
        return  all([
                    any(
                        any(
                            keyword in action.lower()
                            for keyword
                            in  {
                                    "pickup", "grab", "take", "use", "move", "approach", 
                                    "open", "unlock", "interact", "reach", "get"
                                }
                        )
                        for action
                        in episode_actions
                    ),
                    any(
                        pred.name in ["near", "color", "type", "movable", "openable"]
                        for pred
                        in episode_predicates
                    )
                ])
        
    def _all_components_present_(self,
        episode_predicates: PredicateSet
    ) -> bool:
        """# All Components are Present?
    
        Check if all component predicates of this composition pattern are present in the episode 
        predicates.

        ## Args:
            * episode_predicates    (PredicateSet): Predicates from episode.

        ## Returns:
            * bool:
                * True:     All components present.
                * False:    All components not present.
        """
        # Parse the pattern components to find what we're looking for.
        for pattern_string in self.pattern.component_patterns:
            
            # Set flag indicating if negation pattern.
            negated:    bool =  pattern_string.startswith('¬')
            
            # If negated, remove negation symbol.
            if negated: pattern_string = pattern_string[1:].strip()
            
            # Ensure this component pattern matches any episode predicate.
            if not self._component_matches_episode_(
                pattern_string =        pattern_string,
                episode_predicates =    episode_predicates,
                negated =               negated
            ): return False
        
        # All checks passed.
        return True
        
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

    def _component_matches_episode_(self,
        pattern_string:     str,
        episode_predicates: PredicateSet,
        negated:            bool =          False
    ) -> bool:
        """# Does Component Match Episode?
        
        Check if a single component pattern matches predicates in the episode.
        
        ## Args:
            * pattern_string        (str):          Pattern like "near(?agent, ?obj)".
            * episode_predicates    (PredicateSet): Episode predicates.
            * negated               (bool):         Whether this is a negated pattern.
        
        ## Returns:
            * bool:
                * True:     Pattern matches (or doesn't match if negated).
                * False:    Pattern was not matched consistently with predicate.
        """
        # Parse the pattern structure.
        pattern_match:          Optional[Match[str]] =  match(
                                                            pattern =   r'(\w+)\s*\(([^)]*)\)', 
                                                            string =    pattern_string.strip()
                                                        )
        
        # If we can't parse, assume it doesn't match.
        if not pattern_match: return not negated
        
        # Extract predicate name and arguments.
        predicate_name:         str =                   pattern_match.group(1)
        predicate_arguments:    str =                   pattern_match.group(2)
        
        # Parse arguments to identify variables vs constants
        arguments:              List[str] =             [
                                                            argument.strip()
                                                            for argument
                                                            in predicate_arguments.split(',')
                                                        ]                               \
                                                        if predicate_arguments.strip()  \
                                                        else []
        
        # Check if any episode predicate matches this pattern
        matches_found:          bool =                  any(
                                                            self._predicate_matches_pattern_(
                                                                predicate =         episode_predicate,
                                                                pattern_name =      predicate_name,
                                                                pattern_arguments = arguments
                                                            )
                                                            for episode_predicate
                                                            in episode_predicates
                                                        )
        
        # For negated patterns, we want NO matches, at least one match, for regular patterns.
        return not matches_found if negated else matches_found
        
    def _composition_relevant_to_episode_(self,
        episode:    Dict[str, Any]
    ) -> bool:
        """# Is Composition Relevant to Episode?
        
        Check if this composition pattern was relevant to an episode using sophisticated analysis.
        
        A composition is considered relevant if:
            1. All component predicates of the pattern appear in the episode.
            2. The pattern could have been used for decision-making.
            3. The pattern relates to the episode's goals or outcomes.
            4. The temporal context makes the pattern applicable.
        
        This is much more sophisticated than just checking if predicates exist - it determines if 
        the composition was actually meaningful in the context of the episode.

        ## Args:
            * episode   (Dict[str, Any]):   Episode data including predicates, actions, outcomes.

        ## Returns:
            * bool:
                * True:     Composition was relevant and could have been used.
                * False:    Composition was not relevant to this episode.
        """
        # Extract episode components
        episode_predicates: PredicateSet =  episode.get("predicates", PredicateSet())
        episode_actions:    List[str] =     episode.get("actions", [])
        
        # Provide evaluation.
        return  all([
                    # Check 1: Component predicates must be present.
                    self._all_components_present_(
                        episode_predicates =    episode_predicates
                    ),
                    
                    # Check 2: Pattern must be actionable in this context.
                    self._pattern_actionable_in_context_(
                        episode_predicates =    episode_predicates,
                        episode_actions =       episode_actions
                    ),
                    
                    # Check 3: Pattern must relate to episode goals/outcomes.
                    self._pattern_relates_to_outcome_(
                        episode_outcome =       episode.get("outcome", ""),
                        episode_actions =       episode_actions
                    ),
                    
                    # Check 4: Temporal/causal relevance.
                    self._pattern_temporally_relevant_(
                        episode_predicates =    episode_predicates,
                        episode_actions =       episode_actions
                    )
                ])
    
    def _involves_actionable_predicates_(self,
        episode_predicates: PredicateSet
    ) -> bool:
        """# Involves Actionable Predicates?
    
        Check if the episode involves predicates that typically enable actions.

        ## Args:
            * episode_predicates    (PredicateSet): Predicates generated from episode.

        ## Returns:
            * bool:
                * True:     Episode has actionable predicates.
                * False:    Episide does not have actionable predicates.
        """
        return  any(
                    pred.name in    {
                                        "near", "far", "accessible", "blocked", "open", "closed",
                                        "movable", "fixed", "available", "busy", "reachable"
                                    }
                    for pred
                    in episode_predicates
                )
        
    def _pattern_actionable_in_context_(self,
        episode_predicates: PredicateSet,
        episode_actions:    List[str]
    ) -> bool:
        """# Is Pattern Actionable in Context?
        
        Determine if this composition pattern was actionable given the episode context.
        
        A pattern is actionable if:
        * It involves objects/agents that could take actions.
        * The pattern enables or prevents certain actions.
        * The pattern is consistent with the action sequence.
        
        ## Args:
            * episode_predicates    (PredicateSet): Episode predicates.
            * episode_actions       (List[str]):    Actions taken in episode.
        
        ## Returns:
            * bool:
                * True:     Pattern was actionable.
                * False:    Pattern is not actionable.
        """
        # For accessibility patterns (main use case).
        if "accessibility" in self.pattern.name.lower():    return  self._accessibility_pattern_actionable_(
                                                                        episode_predicates =    episode_predicates,
                                                                        episode_actions =       episode_actions
                                                                    )
        
        # For safety patterns.
        elif "safety" in self.pattern.name.lower():         return  self._safety_pattern_actionable_(
                                                                        episode_predicates =    episode_predicates,
                                                                        episode_actions =       episode_actions
                                                                    )
        
        # Otherise, pattern is actionable if it involves common action-related predicates.
        return  self._involves_actionable_predicates_(
                    episode_predicates =    episode_predicates
                )
    
    def _pattern_relates_to_outcome_(self,
        episode_outcome:    str,
        episode_actions:    List[str]
    ) -> bool:
        """# Pattern Relates to Outcome?
    
        Check if this composition pattern relates to the episode's outcome.
        
        A pattern relates to the outcome if:
            * It enables/prevents the observed outcome.
            * It's causally connected to the action sequence.
            * It explains success or failure.

        ## Args:
            * episode_outcome   (str):          What happened in the episode.
            * episode_actions   (List[str]):    Action that were taken during episode.

        ## Returns:
            * bool:
                * True:     Pattern relates to outcome.
                * False:    Pattern does not relate to outcome.
        """
        # For accessibility patterns...
        if "accessibility" in self.pattern.name.lower():
            
            # Relates to outcomes involving object manipulation, unlocking, reaching goals.
            return  any(
                        outcome in episode_outcome.lower() 
                        for outcome
                        in  {
                                "unlock", "open", "reach", "obtain", "get", "pickup", 
                                "success", "goal", "complete", "achieve"
                            }
                    )
        
        # For safety patterns...
        if "safety" in self.pattern.name.lower():
            
            # Relates to navigation outcomes, avoiding danger, path completion.
            return  any(
                        outcome in episode_outcome.lower()
                        for outcome
                        in  {
                                "safe", "danger", "avoid", "navigate", "reach", "arrive",
                                "path", "route", "travel"
                            }
                    )
        
        # Otherwise, assume pattern is relevant if outcome is not empty.
        return len(episode_outcome.strip()) > 0
    
    def _pattern_temporally_relevant_(self,
        episode_predicates: PredicateSet,
        episode_actions:    List[str]
    ) -> bool:
        """# Pattern is Temporally Relevant?
    
        Check if the composition pattern was temporally relevant to the episode.
        
        This ensures the pattern was applicable at the right time during the episode, not just 
        present but irrelevant due to timing.

        ## Args:
            * episode_predicates    (PredicateSet): Episode predicates.
            * episode_actions       (List[str]):    Sequence of episode actions.

        ## Returns:
            * bool:
                * True:     Pattern is temporally relevant.
                * False:    Pattern is not temporally relevant.
        """
        # For most patterns, if all components are present and actionable, we assume temporal relevance.
        
        # Advanced temporal reasoning would consider:
        # - When during the episode the pattern components became true
        # - Whether the pattern was used for decision-making
        # - If the pattern remained relevant throughout the action sequence
        
        # For now, use a simplified heuristic:
        # Pattern is temporally relevant if there are sufficient predicates and actions to indicate 
        # active engagement.
        return  all([
                    len(episode_predicates) >= 2,
                    len(episode_actions)    >= 1
                ])

    def _predicate_matches_pattern_(self,
        predicate:          Predicate,
        pattern_name:       str,
        pattern_arguments:  List[str]
    ) -> bool:
        """# Does Predicate Match Pattern?
        
        Check if a concrete predicate matches a pattern template.
        
        ## Args:
            * predicate         (Predicate):    Concrete predicate from episode.
            * pattern_name      (str):          Expected predicate name.
            * pattern_arguments (List[str]):    Pattern arguments (with variables and constants).
        
        ## Returns:
            * bool: True if predicate matches the pattern.
        """
        # Name must match.
        if predicate.name != pattern_name:                  return False
        
        # Arity must match.
        if len(predicate.arguments) != len(pattern_arguments):   return False
        
        # Check argument compatibility.
        for pred_arg, pattern_arg in zip(predicate.arguments, pattern_arguments):
            
            # Variables (starting with ?) match anything.
            if pattern_arg.startswith('?'): continue
            
            # Constants must match exactly.
            elif pred_arg != pattern_arg:   return False
        
        # All checks passed.
        return True
        
    def _safety_pattern_actionable_(self,
        episode_predicates: PredicateSet,
        episode_actions:    List[str]
    ) -> bool:
        """# Is Safety Pattern Actionable?
    
        Check if safety patterns are actionable in this episode.
        
        ## Args:
            * episode_predicates    (PredicateSet): Episode predicates
            * episode_actions       (List[str]):    Actions taken
        
        ## Returns:
            * bool: True if safety pattern was actionable
        """
        # Safety is actionable if there are navigation or path-related actions.
        return  all([
                    any(
                        any(
                            keyword in action.lower()
                            for keyword
                            in  {
                                    "move", "go", "navigate", "walk", "travel", "path", "route"
                                }
                        )
                        for action in episode_actions
                    ),
                    any(
                        pred.name in ["path", "dangerous", "safe", "blocked", "clear"]
                        for pred
                        in episode_predicates
                    )
                ])
        
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