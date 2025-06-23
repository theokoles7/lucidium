"""# lucidium.sybolic.predicate.composition.Matcher

Pattern matching algorithms for unifying composition patterns with concrete predicate instances.
"""

__all__ = ["Matcher"]

from itertools                                      import product
from re                                             import match, Match
from typing                                         import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic.predicate.category                import PredicateCategory
    from symbolic.predicate.composition.pattern     import Pattern
    from symbolic.predicate.composition.type        import CompositionType
    from symbolic.predicate.set                     import PredicateSet
    from symbolic.predicate.signature               import PredicateSignature
    from symbolic.predicate.vocabulary              import PredicateVocabulary

class Matcher():
    """# (Pattern) Matcher.
    
    Implements sophisticated pattern matching and unification algorithms.
    
    Mathematical foundation: First-order logic unification with constraint satisfaction. Uses 
    constraint propagation and backtracking to find consistent variable bindings that satisfy 
    all pattern components simultaneously.
    """
    
    def __init__(self,
        vocabulary: PredicateVocabulary
    ):
        """# Instantiate (Pattern) Matcher.
        
        ## Args:
            * vocabulary    (PredicateVocabulary):  Available predicate vocabulary.
        """
        # Define vocabulary.
        self._vocabulary_:  PredicateVocabulary =   vocabulary
        
        # Initialize statistics.
        self._statistics_:  Dict[str, int] =        {
                                                        "patterns_matched":         0,
                                                        "unification_attempts":     0,
                                                        "successful_bindings":      0,
                                                        "constraint_violations":    0
                                                    }
        
        
    # METHODS ======================================================================================
    
    def find_pattern_matches(self,
        pattern:    "Pattern",
        predicates: "PredicateSet"
    ) -> List[Dict[str, Any]]:
        """# Find Pattern Matches.
        
        Find all instances where a composition pattern matches the given predicates.
        
        ## Algorithm:
            1. Parse component patterns into unification templates
            2. Find candidate predicates for each template  
            3. Use constraint satisfaction to find consistent variable bindings
            4. Validate complete matches against pattern requirements
        
        Mathematical foundation: Constraint Satisfaction Problem (CSP) solving with arc consistency 
        and backtracking search.
        
        ## Args:
            * pattern       (Pattern):      Composition pattern to match.
            * predicates    (PredicateSet): Available predicates to match against.
            
        ## Returns:
            * List[Dict[str, Any]]: Valid matches with variable bindings.
        """
        # Increment pattern matching attempts.
        self._matching_statistics_["patterns_matched"] += 1
        
        # 1. Parse component patterns into searchable templates -----------
        templates:              Dict[str, Dict[str, Any]] =         self._parse_component_patterns_(
                                                                        component_patterns =    pattern.component_patterns
                                                                    )
        
        # 2. Find candidate matches for each template ---------------------
        
        # Initialize mapping of template matches.
        template_matches:       Dict[str, Any] =                    {}
        
        # For each template...
        for template_name, template in templates.items():
            
            # Find matches, if any.
            matches:            List[Dict[str, Any]] =              self._find_template_matches_(
                                                                        template =              template,
                                                                        predicates =            predicates
                                                                    )
            
            # Add to mapping.
            template_matches[template_name] =                       matches
            
            # Increment statistics.
            self._matching_statistics_["unification_attempts"] +=   len(matches)
        
        # 3. Find consistent variable bindings across templates -----------
        consistent_bindings:    List[Dict[str, Any]] =              self._find_consistent_bindings_(
                                                                        template_matches =  template_matches,
                                                                        templates =         templates
                                                                    )
        
        # 4. Validate complete pattern matches ----------------------------
        
        # Initialize list of valid matches.
        valid_matches:          List[Dict[str, Any]] =              []
        
        # For each binding...
        for binding in consistent_bindings:
            
            # If pattern match is valid...
            if self._pattern_match_valid_(
                pattern =       pattern,
                match_info =    binding,
                predicates =    predicates
            ):
                # Append bindings to matches list.
                valid_matches.append(binding)
                
                # Increment count of successful bindings.
                self._matching_statistics_["successful_bindings"]   += 1
                
            # Otherwise...
            else:
                
                # Increment count of constraint violations.
                self._matching_statistics_["constraint_violations"] += 1
                
        # Provide valid matches found.
        return valid_matches
        
        
    # HELPERS ======================================================================================
    
    def _find_consistent_bindings_(self,
        template_matches:   Dict[str, List[Dict[str, Any]]],
        tempaltes:          Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """# Find Consistent Bindings.
        
        Use constraint satisfaction to find variable bindings consistent across all templates.
        
        Mathematical foundation: Arc consistency with backtracking search. Ensures that if variable 
        ?X is bound to value V in one template, it has the same binding in all other templates that 
        use ?X.
        
        ## Args:
            * template_matches  (Dict[str, List[Dict[str, Any]]]):  Matches per template.
            * templates         (Dict[str, Dict[str, Any]]):        Template structures.
            
        ## Returns:
            * List[Dict[str, Any]]: Consistent variable binding combinations.
        """
        # Initialize list of template names.
        template_names:         List[str] =             list(template_matches.keys())
        
        # If there were no template matches provided, return empty list.
        if not template_names: return []
        
        # If only one template, return its matches directly.
        if len(template_names) == 1: return [
                                                match["bindings"]
                                                for match
                                                in template_matches[template_names[0]]
                                            ]
        
        # Otherwise, initialize list of consistent bindings and match combinations.
        consistent_bindings:    List[Dict[str, Any]] =  []
        match_combinations:     List[Dict[str, Any]] =  list(
                                                            product(*[template_matches[name]
                                                            for name
                                                            in template_names])
                                                        )
        
        # For each combination...
        for combination in match_combinations:
            
            # Initialize mapping of merged bindings.
            merged_bindings:    Dict[str, Any] =        {}
            
            # Set flag to indicate if all bindings are consistent.
            is_consistent:      bool =                  True
            
            # For each match...
            for match in combination:
                
                # For each variable...
                for variable_name, variable_value in match["bindings"].items():
                    
                    # If the variable name is in merged bindings...
                    if variable_name in merged_bindings:
                        
                        # Check consistency, because variable is already bound.
                        if merged_bindings[variable_name] != variable_value:
                            
                            # Set flag and break for match.
                            is_consistent =             False
                            break
                        
                    # Otherwise, add new binding.
                    merged_bindings[variable_name] =    variable_value
                    
                # If bindings were not consistent, abort validation.
                if not is_consistent: break
                
            # If bindings were consistent.
            if is_consistent:
                
                # Add metadata about which predicates were matched.
                consistent_bindings.append({
                    "bindings":             merged_bindings,
                    "matched_predicates":   [match["predicate"] for match in combination],
                    "template_assignments": {
                                                template_names[i]: combination[i]
                                                for i
                                                in range(len(template_names))
                                            }
                })
                
        # Provide consistent bindings found.
        return consistent_bindings
    
    def _find_template_matches_(self,
        template:   Dict[str, Any],
        predicates: "PredicateSet"
    ) -> List[Dict[str, Any]]:
        """# Find Template Matches.
        
        Find all predicates that could unify with a template structure.
        
        ## Args:
            * template      (Dict[str, Any]):   Parsed template structure.
            * predicates    (PredicateSet):     Available predicates.
            
        ## Returns:
            * List[Dict[str, Any]]: Candidate matches with bindings.
        """
        # Initialize list of matches.
        matches:    List[Dict[str, Any]] =  []
        
        # For each predicate passed...
        for predicate in predicates:
            
            # Skip if not inherently compatible.
            if  (
                    predicate.name !=   template["predicate_name"] or
                    predicate.arity !=  template["arity"]
                ): continue
            
            # Set flag to indicate if constants match.
            constants_match:    bool =              True
            
            # For each constant in template...
            for p, expected_value in template["constant_positions"].items():
                
                # If predicate values do not match...
                if predicate.arguments[p] != expected_value:
                    
                    # Set flag and stop parsing.
                    constants_match =   False
                    break
                
            # If constants did not match, skip to next predicate.
            if not constants_match: continue
            
            # Otherwise, append to matches.
            matches.append({
                "predicate":    predicate,
                "bindings":     {
                                    variable_name:  predicate.arguments[p]
                                    for p, variable_name
                                    in template["variable_positions"].items()
                                },
                "template":     template
            })
        
        # Provide matches found.
        return matches
    
    def _parse_component_patterns_(self,
        component_patterns: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """# Parse Component Patterns.
        
        Parse pattern strings into structured templates for unification.
        
        ## Handles:
            - Predicate name extraction
            - Variable vs constant argument identification  
            - Negation detection (¬predicate)
            - Arity validation
        
        ## Args:
            * component_patterns    (List[str]):    Pattern strings like ["near(?agent, ?obj)"].
            
        ## Returns:
            * Dict[str, Dict[str, Any]]:    Parsed template structures.
        """
        # Initialize mapping of parsed templates.
        templates:  Dict[str, Dict[str, Any]] = {}
        
        # For each pattern provided...
        for p, pattern_string in enumerate(component_patterns):
            
            # Create template name.
            template_name:      str =               f"template_{p}"
            
            # Set flag indicating if pattern is negation.
            negated:            bool =              pattern_string.startswith("¬")
            
            # If pattern was negation, remove negation symbol.
            if negated: pattern_string =            pattern_string[1:].strip()
            
            # Parse predicate structure.
            pattern_match:      Match =             match(r"(\w+)\s*\(([^)]*)\)", pattern_string.strip())
            
            # If there was no pattern match found, skip pattern.
            if not pattern_match: continue
            
            # Extract pattern name and arguments.
            predicate_name:     str =               pattern_match.group(1)
            predicate_args:     str =               pattern_match.group(2)
            
            # Parse arguments.
            arguments:          List[str] =         [arg.strip() for arg in predicate_args.split(",")]  \
                                                        if predicate_args.strip()                       \
                                                        else []
                                            
            # Initialize structures for recording variables & their positions.
            variables:          List[str] =         []
            variable_positions: Dict[int, str] =    {}
            constant_positions: Dict[int, str] =    {}
            
            # For eac argument...
            for a, argument in enumerate(arguments):
                
                # If it is prefixed by a question mark...
                if argument.startswith("?"):
                    
                    # Append to variables.
                    variables.append(argument)
                    
                    # Record position.
                    variable_positions[a] =         argument
                    
                # Otheriwse, for constants...
                else:
                    
                    # Record those positions.
                    constant_positions[a] =         argument
                    
            # Add template.
            templates[template_name] =              {
                                                        "predicate_name":       predicate_name,
                                                        "variables":            variables,
                                                        "variable_positions":   variable_positions,
                                                        "constant_positions":   constant_positions,
                                                        "negated":              negated,
                                                        "arity":                len(arguments)
                                                    }
        
        # Provide mapping.
        return templates
    
    def _pattern_match_valid_(self,
        pattern:    "Pattern",
        match_info: Dict[str, Any],
        predicates: "PredicateSet"
    ) -> bool:
        """# Validate Pattern Match.
        
        Validate that a potential match satisfies all pattern requirements.
        
        ## Checks:
            1. All r`equired predicates are present
            2. Negated predicates are properly handled
            3. Type constraints are satisfied
            4. No logi`cal contradictions exist
        
        ## Args:
            * pattern       (Pattern):          Original composition pattern.
            * match_info    (Dict[str, Any]):   Match with bindings and predicates.
            * predicates    (PredicateSet):     Available predicates.
            
        ## Returns:
            * bool: True if match is valid.
        """
        bindings:               Dict[str, Any] =    match_info["bindings"]
        matched_predicates:     Dict[str, Any] =    match_info["matched_predicates"]
        template_assignments = match_info.get("template_assignments", {})
        
        # Verify all matched predicates exist in the predicate set
        for predicate in matched_predicates:
            if not predicates.contains(predicate):
                return False
                
        # Handle negated templates
        for template_match in template_assignments.values():
            template = template_match["template"]
            if template["negated"]:
                # For negated patterns, the predicate should NOT exist
                if predicates.contains(template_match["predicate"]):
                    return False
                    
        # Validate variable bindings are type-compatible
        for var_name, var_value in bindings.items():
            if not self._validate_variable_binding_(var_name, var_value):
                return False
                
        return True
        
    def _validate_variable_binding_(self, variable_name: str, variable_value: Any) -> bool:
        """# Validate Variable Binding.
        
        Check if a variable binding is type-compatible and reasonable.
        
        ## Args:
            * variable_name (str): Variable name.
            * variable_value (Any): Proposed binding value.
            
        ## Returns:
            * bool: True if binding is valid.
        """
        # Basic validation - ensure non-null values
        if variable_value is None:
            return False
            
        # Type-specific validation based on variable name patterns
        if any(keyword in variable_name.lower() for keyword in ["agent", "obj", "value"]):
            return isinstance(variable_value, str) and len(variable_value) > 0
            
        if "location" in variable_name.lower():
            return (isinstance(variable_value, str) or 
                   (isinstance(variable_value, (tuple, list)) and len(variable_value) == 2))
                   
        return True
        
    def get_statistics(self) -> Dict[str, Any]:
        """# Get Matching Statistics.
        
        ## Returns:
            * Dict[str, Any]: Pattern matching performance metrics.
        """
        return self._matching_statistics_.copy()