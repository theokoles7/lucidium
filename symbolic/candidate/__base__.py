"""# lucidium.symbolic.candidate.Candidate

Define structure and functionality for a candidate solution in the symbolic search space.
"""

from typing                             import Any, Dict, TYPE_CHECKING

from symbolic.candidate.evaluation      import Evaluator
from symbolic.candidate.evidence        import Evidence
from symbolic.candidate.validation      import Validator

if TYPE_CHECKING:
    from symbolic.composition.pattern   import Pattern
    from symbolic.logic                 import Expression

class Candidate():
    """# Candidate.
    
    A candidate composition discovered from experience data.
    
    Mathematical foundation: A candidate represents a hypothesis H about a logical composition
    that we're testing through statistical evidence collection. The candidate tracks:
    
        - Hypothesis H: pattern → definition (logical implication)
        - Evidence E: {positive_instances, negative_instances}
        - Metrics M: {confidence, support, utility} computed from E
    
    Promotion occurs when statistical thresholds are met:
    support(H) ≥ min_support ∧ confidence(H) ≥ min_confidence
        
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
        pattern:    "Pattern",
        definition: "Expression"
    ):
        """# Instantiate Candidate.

        ## Args:
            * pattern       (Pattern):      Composition pattern this candidate represents.
            * definition    (Expression):   Formal logical definition of the composition.
        """
        # Define core properties.
        self._pattern_:     "Pattern" =     pattern
        self._definition_:  "Expression" =  definition
        
        # Instantiate sub-systems.
        self._evaluator_:   Evaluator =     Evaluator()
        self._evidence_:    Evidence =      Evidence()
        self._validator_:   Validator =     Validator()
        
        
    # PROPERTIES ===================================================================================
    
    @property
    def co_occurrence(self) -> float:
        """# Co-Occurrence.
        
        P(all pattern components present | any pattern component present)
        Measures the statistical association strength between pattern components.
        """
        return self._evaluator_.co_occurrence
    
    @property
    def confidence(self) -> float:
        """# Confidence.
        
        Confidence: P(pattern is correct | pattern appears) = support / (support + counter_examples)
        Mathematical range: [0, 1] where 1 = pattern is always correct when it appears.
        """
        return  self._evaluator_.calculate_confidence(
                    positive_evidence_count =   len(self._evidence_.positive_instances),
                    total_evidence_count =      self._evidence_.total_evidence_count
                )
    
    @property
    def definition(self) -> "Expression":
        """# Expression.
        
        The formal logical expression that defines the semantics of this composition.
        In standard logic notation: pattern_components → composite_predicate
        """
        return self._definition_
    
    @property
    def distinctiveness(self) -> float:
        """# Distinctiveness.
        
        Measures how much novel information this pattern provides compared to existing knowledge.
        Based on information theory: more distinctive patterns have higher information gain.
        """
        return self._evaluator_.distinctiveness
    
    @property
    def meets_promotion_criteria(self) -> bool:
        """# Meets Promotion Criteria?
        
        Mathematical condition for promotion:
        support(H) ≥ min_support ∧ confidence(H) ≥ min_confidence
        
        Where H is the hypothesis represented by this candidate.
        """
        return  self._validator_.meets_promotion_criteria(
                    support =       self.support,
                    confidence =    self.confidence,
                    pattern =       self.pattern
                )
    
    @property
    def pattern(self) -> "Pattern":
        """# Pattern.
        
        The pattern template that defines the structure of this composition hypothesis.
        """
        return self._pattern_
    
    @property
    def support(self) -> int:
        """# Support.
        
        Support count: |{instances where pattern holds}|
        This is the absolute frequency of the pattern in the evidence set.
        Higher support indicates the pattern occurs frequently enough to be meaningful.
        """
        return len(self._evidence_.positive_instances)
    
    @property
    def utility(self) -> float:
        """# Utility.
        
        Utility: P(goal achieved | pattern is correct)
        This measures the practical value of the pattern for decision-making.
        """
        return  self._evaluator_.calculate_utility(
                    positive_evidence_count =   len(self._evidence_.positive_instances),
                    total_evidence_count =      self._evidence_.total_evidence_count
                )
    
    
    # METHODS ======================================================================================
    
    def add_evidence(self,
        instance:       Dict[str, Any],
        is_positive:    bool
    ) -> None:
        """# Add Evidence.
        
        Add a single piece of evidence supporting or contradicting this hypothesis.
        
        ## Args:
            * instance      (Dict[str, Any]):   Evidence instance with context and outcome.
            * is_positive   (bool):             True if evidence supports the hypothesis.
        """
        if is_positive: self._evidence_.add_positive_instance(instance = instance)
        else:           self._evidence_.add_negative_instance(instance = instance)
        
    def update_advanced_metrics(self,
        co_occurrence:      float,
        distinctiveness:    float
    ) -> None:
        """# Update Advanced Metrics.
        
        Update metrics that require external computation (e.g., from the composition engine).
        
        ## Args:
            * co_occurrence     (float):    How often pattern components appear together.
            * distinctiveness   (float):    How unique this pattern is vs existing knowledge.
        """
        self._evaluator_.co_occurrence =    co_occurrence
        self._evaluator_.distinctiveness =  distinctiveness