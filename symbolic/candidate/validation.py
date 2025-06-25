"""# lucidium.symbolic.candidate.Validator

Validate pattern relevance and promotion criteria for composition candidates.
"""

__all__ = ["Validator"]

from re                                 import match, Match
from typing                             import List, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic.composition.pattern   import Pattern
    from symbolic.predicate             import Predicate, PredicateSet

class Validator():
    """# (Pattern) Validator.
    
    Implements validation logic based on:
        - Association rule mining thresholds (support, confidence)
        - Logical coherence checking
        - Episodic relevance analysis
    
    Mathematical foundation: Statistical hypothesis testing for pattern validity.
    """
        
    
    # METHODS ======================================================================================
    
    def meets_promotion_criteria(self,
        support:    int,
        confidence: float,
        pattern:    "Pattern"
    ) -> bool:
        """# (Pattern) Meets Promotion Criteria?
        
        Mathematical condition for promotion based on association rule mining:
        support(pattern) ≥ min_support ∧ confidence(pattern) ≥ min_confidence
        
        ## Args:
            * support       (int):      Number of positive evidence instances.
            * confidence    (float):    Confidence score [0, 1].
            * pattern       (Pattern):  Pattern object with thresholds.

        ## Returns:
            * bool: True if statistical criteria are met.
        """
        return  all([
                    # Support is above threshold.
                    support     >= pattern.minimum_support,
                    
                    # Confidence is above theshold.
                    confidence  >= pattern.confidence_threshold
                ])
        
    def validate_actionability(self,
        pattern_name:       str,
        episode_predicates: "PredicateSet",
        episode_actions:    List[str]
    ) -> bool:
        """# Validate Actionability.
        
        Check if a pattern was actionable in the given episode context.
        A pattern is actionable if it could influence decision-making.
        
        ## Args:
            * pattern_name          (str):          Name of the pattern.
            * episode_predicates    (PredicateSet): Predicates in episode.
            * episode_actions       (List[str]):    Actions taken in episode.

        ## Returns:
            * bool: True if pattern was actionable.
        """
        # Dispatch to specialized actionability checkers.
        if "accessibility" in pattern_name.lower():
            
            return  self._check_accessibility_actionability_(
                        predicates =    episode_predicates,
                        actions =       episode_actions
                    )
            
        elif "safety"  in pattern_name.lower():
            
            return  self._check_safety_actionability_(
                        predicates =    episode_predicates,
                        actions =       episode_actions
                    )
        else:
            
            return  self._check_general_actionability_(
                        predicates =    episode_predicates
                    )
        
    def validate_pattern_in_episode(self,
        pattern_components: List[str],
        episode_predicates: "PredicateSet"
    ) -> bool:
        """# Validate Pattern in Episode.
        
        Check if all pattern components can be satisfied in the given episode.
        Handles both positive and negative literals (¬predicate).
        
        ## Args:
            * pattern_components    (List[str]):    Component patterns to validate.
            * episode_predicates    (PredicateSet): Available predicates.

        ## Returns:
            * bool: True if all components can be satisfied.
        """
        return  all(
                    self._component_satisfiable_(
                        pattern_string =        component,
                        episode_predicates =    episode_predicates
                    )
                    for component
                    in pattern_components
                )
        
                        
    # HELPERS ======================================================================================
    
    def _check_accessibility_actionability_(self,
        predicates: "PredicateSet",
        actions:    List[str]
    ) -> bool:
        """# Check Accessibility Actionability.
        
        Check if an accessibility pattern was actionable in the given episode context.
        A pattern is actionable if it could influence decision-making.
        
        ## Args:
            * predicates    (PredicateSet): Predicates in episode.
            * actions       (List[str]):    Actions taken in episode.

        ## Returns:
            * bool: True if pattern was actionable.
        """
        # Indicate that the actions in the episode...
        return  all([
                    # Included manipulation actions...
                    any(
                        keyword in action.lower()
                        for action
                        in actions
                        for keyword 
                        in {
                            "pickup", "grab", "take", "use", "move", "approach", 
                            "open", "unlock", "interact", "reach", "get"
                        }
                    ),
                    
                    # And had spatial predicates.
                    any(
                        predicate.name in ["near", "color", "type", "movable", "openable"]
                        for predicate
                        in predicates
                    )
                ])
        
    def _check_general_actionability_(self,
        predicates: "PredicateSet"
    ) -> bool:
        """# Check General Actionability.
        
        Check if a general pattern was actionable in the given episode context.
        A pattern is actionable if it could influence decision-making.

        ## Args:
            * predicates    (PredicateSet): Predicates in episode.

        ## Returns:
            * bool: True if pattern was actionable.
        """
        return  any(
                    predicate.name in   {
                                            "near", "far", "accessible", "blocked", "open", "closed",
                                            "movable", "fixed", "available", "busy", "reachable"
                                        }
                    for predicate
                    in predicates
        )
    
    def _check_safety_actionability_(self,
        predicates: "PredicateSet",
        actions:    List[str]
    ) -> bool:
        """# Check Safety Actionability.
        
        Check if an safety pattern was actionable in the given episode context.
        A pattern is actionable if it could influence decision-making.
        
        ## Args:
            * predicates    (PredicateSet): Predicates in episode.
            * actions       (List[str]):    Actions taken in episode.

        ## Returns:
            * bool: True if pattern was actionable.
        """
        # Indicate that the actions in the episode...
        return  all([
                    # Included navigation actions...
                    any(
                        keyword in action.lower()
                        for action
                        in actions
                        for keyword 
                        in {
                            "move", "go", "navigate", "walk", "travel", "path", "route"
                        }
                    ),
                    
                    # And had safety predicates.
                    any(
                        predicate.name in ["path", "dangerous", "safe", "blocked", "clear"]
                        for predicate
                        in predicates
                    )
                ])
    
    def _component_satisfiable_(self,
        pattern_string:     str,
        episode_predicates: "PredicateSet"
    ) -> bool:
        """# (Is) Component Satisfiable?
        
        Check if a single pattern component can be satisfied.
        Supports negation: ¬predicate(args) means predicate should NOT be present.
        
        ## Args:
            * pattern_string        (str):          Pattern like "near(?agent, ?obj)" or 
                                                    "¬dangerous(?x, ?y)".
            * episode_predicates    (PredicateSet): Available predicates.

        ## Returns:
            * bool: True if component can be satisfied.
        """
        # Set flag to indicate negation.
        negation:       bool =      pattern_string.startswith("¬")
        
        # If pattern is negation, remove negation symbol.
        if negation: pattern_string = pattern_string[1:].strip()
        
        # Parse predicate structure.
        pattern_match:  Match =     match(r'(\w+)\s*\(([^)]*)\)', pattern_string.strip())
        
        # If parsing was not possible, assume pattern does not match.
        if not pattern_match: return not negation
        
        # Extract predicate name and arguments.
        predicate_name: str =       pattern_match.group(1)
        predicate_args: str =       pattern_match.group(2)
        
        # Parse arguments.
        arguments:      List[str] = [
                                        argument.strip()
                                        for argument
                                        in arguments
                                    ] if arguments.strip() else []
        
        # Check if any episode predicates match this pattern.
        matches_found:  bool =      any(
                                        self._predicate_matches_template_(
                                            predicate =             predicate,
                                            template_name =         predicate_name,
                                            template_arguments =    predicate_args
                                        )
                                        for predicate
                                        in episode_predicates
                                    )
        
        # For negated patterns, we want no matches; for regular patterns, we want at least one.
        return not matches_found if negation else matches_found
    
    def _predicate_matches_template_(self,
        predicate:          "Predicate",
        template_name:      str,
        template_arguments: List[str]
    ) -> bool:
        """# Predicate Matches Template?
        
        Check if a concrete predicate matches a pattern template using unification rules.
        
        Unification rules:
            - Variables (?var) can unify with any concrete value
            - Constants must match exactly
            - Predicate names must match exactly
            - Arity must match exactly
        
        ## Args:
            * predicate     (Predicate):    Concrete predicate instance.
            * template_name (str):          Expected predicate name.
            * template_args (List[str]):    Template arguments (may contain variables).

        ## Returns:
            * bool: True if unification is possible.
        """
        # If the predicate's...
        if  (
                # Name does not match, or...
                predicate.name              != template_name            or
                
                # Arguments are consistent with template..
                len(predicate.arguments)    != len(template_arguments)
        ):
            # Then it is not a match.
            return False
        
        # For each of the arguments...
        for predicate_argument, template_argument in zip(predicate.arguments, template_arguments):
            
            # Variables can unify with anything, ...
            if template_argument.startswith("?"): continue
            
            # But constants must match.
            elif str(predicate_argument) != template_argument: return False
            
        # By now, predicate is confirmed to match template.
        return True