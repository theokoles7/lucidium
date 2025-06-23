"""# lucidium.symbolic.predicate.composition.engine.promotion

Candidate evaluation and promotion logic for creating composite predicates.
"""

from typing import Any, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic.candidate import Candidate
    from symbolic.predicate import PredicateVocabulary
    from symbolic.predicate.composition.signature import CompositePredicateSignature

class CandidatePromoter:
    """# Candidate Promoter.
    
    Evaluates composition candidates and promotes qualified ones to actual composite predicates.
    
    Mathematical foundation: Statistical hypothesis testing and association rule mining.
    Uses confidence intervals, significance testing, and utility analysis to determine
    when candidates have sufficient evidence for promotion to the predicate vocabulary.
    """
    
    def __init__(self, vocabulary: 'PredicateVocabulary', minimum_utility_threshold: float = 0.1):
        """# Instantiate Candidate Promoter.
        
        ## Args:
            * vocabulary (PredicateVocabulary): Predicate vocabulary for adding new predicates.
            * minimum_utility_threshold (float): Minimum utility required for promotion.
        """
        self._vocabulary_ = vocabulary
        self._minimum_utility_threshold_ = minimum_utility_threshold
        self._promotion_statistics_ = {
            "candidates_evaluated": 0,
            "candidates_promoted": 0,
            "promotion_failures": 0,
            "average_promotion_confidence": 0.0,
            "utility_calculations": 0
        }
        
    def calculate_advanced_metrics(self, candidate: 'Candidate') -> Tuple[float, float]:
        """# Calculate Advanced Metrics.
        
        Calculate sophisticated statistical metrics for candidate evaluation.
        
        Metrics computed:
        - Co-occurrence: Statistical association strength between pattern components
        - Distinctiveness: Information-theoretic measure of pattern novelty
        
        Mathematical foundation: 
        - Co-occurrence: P(all components present | any component present)
        - Distinctiveness: Weighted combination of complexity, diversity, and predictive power
        
        ## Args:
            * candidate (Candidate): Candidate to evaluate.
            
        ## Returns:
            * Tuple[float, float]: (co_occurrence, distinctiveness) scores.
        """
        self._promotion_statistics_["candidates_evaluated"] += 1
        
        # Calculate co-occurrence strength
        co_occurrence = self._calculate_co_occurrence_strength_(candidate)
        
        # Calculate pattern distinctiveness  
        distinctiveness = self._calculate_pattern_distinctiveness_(candidate)
        
        return co_occurrence, distinctiveness
        
    def _calculate_co_occurrence_strength_(self, candidate: 'Candidate') -> float:
        """# Calculate Co-Occurrence Strength.
        
        Measure how often pattern components appear together vs separately.
        
        Mathematical formula: P(A ∩ B ∩ ... ∩ N) / P(A ∪ B ∪ ... ∪ N)
        Where A, B, ..., N are the pattern components.
        
        ## Args:
            * candidate (Candidate): Candidate to analyze.
            
        ## Returns:
            * float: Co-occurrence strength [0, 1].
        """
        # Access evidence through the candidate's evidence manager
        all_instances = (candidate._evidence_manager_.positive_instances + 
                        candidate._evidence_manager_.negative_instances)
        
        if not all_instances:
            return 0.0
            
        # Count instances where all pattern components are present
        complete_pattern_count = 0
        expected_components = len(candidate.pattern.component_patterns)
        
        for instance in all_instances:
            matched_predicates = instance.get('matched_predicates', [])
            if len(matched_predicates) >= expected_components:
                complete_pattern_count += 1
                
        return complete_pattern_count / len(all_instances)
        
    def _calculate_pattern_distinctiveness_(self, candidate: 'Candidate') -> float:
        """# Calculate Pattern Distinctiveness.
        
        Measure how unique and informative this pattern is compared to existing knowledge.
        
        Combines three factors:
        1. Pattern complexity (structural sophistication)
        2. Binding diversity (generalization across different objects)  
        3. Predictive power (better than random performance)
        
        Mathematical foundation: Information theory and statistical learning theory.
        
        ## Args:
            * candidate (Candidate): Candidate to analyze.
            
        ## Returns:
            * float: Distinctiveness score [0, 1].
        """
        # Factor 1: Pattern structural complexity
        pattern_complexity = self._calculate_structural_complexity_(candidate)
        
        # Factor 2: Variable binding diversity
        binding_diversity = self._calculate_binding_diversity_(candidate)
        
        # Factor 3: Predictive power beyond random chance
        predictive_power = max(0.0, candidate.confidence - 0.5) * 2.0  # Normalize to [0,1]
        
        # Weighted combination (equal weights for simplicity)
        distinctiveness = (pattern_complexity + binding_diversity + predictive_power) / 3.0
        
        return min(1.0, max(0.0, distinctiveness))  # Clamp to valid range
        
    def _calculate_structural_complexity_(self, candidate: 'Candidate') -> float:
        """# Calculate Structural Complexity.
        
        Measure the structural sophistication of the composition pattern.
        
        ## Args:
            * candidate (Candidate): Candidate to analyze.
            
        ## Returns:
            * float: Complexity score [0, 1].
        """
        # Use the candidate's evaluator for complexity calculation
        return candidate._evaluator_.calculate_pattern_complexity(
            candidate.pattern.component_patterns
        )
        
    def _calculate_binding_diversity_(self, candidate: 'Candidate') -> float:
        """# Calculate Binding Diversity.
        
        Measure how many different variable binding combinations this pattern covers.
        
        ## Args:
            * candidate (Candidate): Candidate to analyze.
            
        ## Returns:
            * float: Diversity score [0, 1].
        """
        # Use the candidate's evaluator for diversity calculation
        all_instances = (candidate._evidence_manager_.positive_instances + 
                        candidate._evidence_manager_.negative_instances)
        
        return candidate._evaluator_.calculate_binding_diversity(all_instances)
        
    def create_composite_predicate(self, candidate: 'Candidate') -> bool:
        """# Create Composite Predicate.
        
        Promote a validated candidate to an actual composite predicate in the vocabulary.
        
        Process:
        1. Create composite predicate signature with component information
        2. Add signature to the predicate vocabulary
        3. Update promotion statistics
        4. Handle creation failures gracefully
        
        ## Args:
            * candidate (Candidate): Validated candidate ready for promotion.
            
        ## Returns:
            * bool: True if predicate was successfully created.
        """
        from symbolic.predicate.composition.signature import CompositePredicateSignature
        from symbolic.predicate import PredicateCategory
        
        try:
            # Create composite predicate signature
            composite_signature = CompositePredicateSignature(
                name=candidate.pattern.result_signature.name,
                argument_types=candidate.pattern.result_signature.arg_types,
                component_predicates=[],  # Could be populated with component signatures
                definition=candidate.definition,
                category=PredicateCategory.COMPOSITE,
                description=candidate.pattern.description
            )
            
            # Add to vocabulary
            success = self._vocabulary_.add_signature(composite_signature)
            
            if success:
                # Update promotion statistics
                self._promotion_statistics_["candidates_promoted"] += 1
                
                # Update average confidence (running average)
                current_avg = self._promotion_statistics_["average_promotion_confidence"]
                promoted_count = self._promotion_statistics_["candidates_promoted"]
                new_avg = ((current_avg * (promoted_count - 1)) + candidate.confidence) / promoted_count
                self._promotion_statistics_["average_promotion_confidence"] = new_avg
                
                return True
            else:
                self._promotion_statistics_["promotion_failures"] += 1
                return False
                
        except Exception as e:
            print(f"Error creating composite predicate: {e}")
            self._promotion_statistics_["promotion_failures"] += 1
            return False
            
    def evaluate_promotion_readiness(self, candidate: 'Candidate') -> Dict[str, Any]:
        """# Evaluate Promotion Readiness.
        
        Comprehensive evaluation of whether a candidate is ready for promotion.
        
        Returns detailed analysis including:
        - Statistical criteria satisfaction
        - Quality metrics
        - Recommendation and reasoning
        
        ## Args:
            * candidate (Candidate): Candidate to evaluate.
            
        ## Returns:
            * Dict[str, Any]: Detailed evaluation results.
        """
        evaluation = {
            "ready_for_promotion": False,
            "criteria_met": {},
            "quality_metrics": {},
            "recommendation": "",
            "reasoning": []
        }
        
        # Check statistical criteria
        support_met = candidate.support >= candidate.pattern.minimum_support
        confidence_met = candidate.confidence >= candidate.pattern.confidence_threshold
        utility_met = candidate.utility >= self._minimum_utility_threshold_
        
        evaluation["criteria_met"] = {
            "support": support_met,
            "confidence": confidence_met,  
            "utility": utility_met
        }
        
        # Calculate quality metrics
        co_occurrence, distinctiveness = self.calculate_advanced_metrics(candidate)
        evaluation["quality_metrics"] = {
            "support": candidate.support,
            "confidence": candidate.confidence,
            "utility": candidate.utility,
            "co_occurrence": co_occurrence,
            "distinctiveness": distinctiveness
        }
        
        # Determine overall readiness
        all_criteria_met = support_met and confidence_met and utility_met
        high_quality = co_occurrence >= 0.6 and distinctiveness >= 0.4
        
        evaluation["ready_for_promotion"] = all_criteria_met and high_quality
        
        # Generate recommendation and reasoning
        if evaluation["ready_for_promotion"]:
            evaluation["recommendation"] = "PROMOTE"
            evaluation["reasoning"].append("All statistical criteria met")
            evaluation["reasoning"].append("High quality metrics achieved")
        else:
            evaluation["recommendation"] = "WAIT"
            if not support_met:
                evaluation["reasoning"].append(f"Insufficient support: {candidate.support} < {candidate.pattern.minimum_support}")
            if not confidence_met:
                evaluation["reasoning"].append(f"Low confidence: {candidate.confidence:.3f} < {candidate.pattern.confidence_threshold}")
            if not utility_met:
                evaluation["reasoning"].append(f"Low utility: {candidate.utility:.3f} < {self._minimum_utility_threshold_}")
            if co_occurrence < 0.6:
                evaluation["reasoning"].append(f"Weak co-occurrence: {co_occurrence:.3f} < 0.6")
            if distinctiveness < 0.4:
                evaluation["reasoning"].append(f"Low distinctiveness: {distinctiveness:.3f} < 0.4")
                
        return evaluation
        
    def get_promotion_recommendations(self, candidates: Dict[str, 'Candidate']) -> List[Dict[str, Any]]:
        """# Get Promotion Recommendations.
        
        Analyze all candidates and provide ranked promotion recommendations.
        
        ## Args:
            * candidates (Dict[str, Candidate]): All active candidates.
            
        ## Returns:
            * List[Dict[str, Any]]: Ranked promotion recommendations.
        """
        recommendations = []
        
        for candidate_id, candidate in candidates.items():
            evaluation = self.evaluate_promotion_readiness(candidate)
            evaluation["candidate_id"] = candidate_id
            evaluation["pattern_name"] = candidate.pattern.name
            recommendations.append(evaluation)
            
        # Sort by readiness and then by quality score
        def quality_score(rec):
            metrics = rec["quality_metrics"]
            return (metrics["confidence"] + metrics["utility"] + 
                   metrics["co_occurrence"] + metrics["distinctiveness"]) / 4.0
            
        recommendations.sort(
            key=lambda x: (x["ready_for_promotion"], quality_score(x)), 
            reverse=True
        )
        
        return recommendations
        
    def get_statistics(self) -> Dict[str, Any]:
        """# Get Promotion Statistics.
        
        ## Returns:
            * Dict[str, Any]: Candidate promotion performance metrics.
        """
        return self._promotion_statistics_.copy()