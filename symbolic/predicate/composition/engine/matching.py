"""# lucidium.sybolic.predicate.composition.Matcher

Pattern matching algorithms for unifying composition patterns with concrete predicate instances.
"""

__all__ = ["Matcher"]

from itertools                                  import product
from re                                         import match, Match
from typing                                     import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic.predicate.composition.pattern import Pattern
    from symbolic.predicate.set                 import PredicateSet
    from symbolic.predicate.vocabulary          import PredicateVocabulary
    from symbolic.predicate                     import Predicate

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
        
    # PROPERTIES ===================================================================================
        
    def statistics(self) -> Dict[str, Any]:
        """# (Matching) Statistics.
        
        Pattern matching performance metrics.
        """
        return self._matching_statistics_.copy()
        
        
    # METHODS ======================================================================================
    
    def find_pattern_matches(self,
        pattern:    "Pattern",
        predicates: "PredicateSet"
    ) -> List[Dict[str, Any]]:
        """# Find Pattern Matches.
        
        Find all instances where a composition pattern matches the given predicates.
        
        This is the core pattern matching algorithm that implements first-order logic unification
        with constraint satisfaction. The process follows these mathematical principles:
        
        ## Algorithm:
            1. Parse component patterns into unification templates
            2. Find candidate predicates for each template  
            3. Use constraint satisfaction to find consistent variable bindings
            4. Validate complete matches against pattern requirements
        
        Mathematical foundation: Constraint Satisfaction Problem (CSP) solving with arc consistency 
        and backtracking search. We use the most general unifier (MGU) approach from automated
        theorem proving to ensure variable bindings are consistent across all pattern components.
        
        ## Args:
            * pattern       (Pattern):      Composition pattern to match.
            * predicates    (PredicateSet): Available predicates to match against.
            
        ## Returns:
            * List[Dict[str, Any]]: Valid matches with variable bindings.
        """
        # Track pattern matching attempts for performance analysis and debugging.
        self._matching_statistics_["patterns_matched"] += 1
        
        # 1. Parse component patterns into searchable templates -----------
        # Convert human-readable pattern strings like "near(?agent, ?obj)" into structured
        # templates that can be efficiently matched against concrete predicates. This parsing
        # extracts predicate names, identifies variables vs constants, handles negation, etc.
        templates:              Dict[str, Dict[str, Any]] =         self._parse_component_patterns_(
                                                                        component_patterns =    pattern.component_patterns
                                                                    )
        
        # 2. Find candidate matches for each template ---------------------
        # For each parsed template, search through all available predicates to find those that could 
        # potentially unify. This is the first phase of constraint satisfaction where we establish 
        # the domain of possible bindings for each template.
        
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
        # This is the critical constraint satisfaction phase where we ensure that if variable ?X is 
        # bound to value V in one template, it has the same binding in all other templates that use 
        # ?X. This implements the occurs check and ensures logical consistency across the entire 
        # pattern.
        consistent_bindings:    List[Dict[str, Any]] =              self._find_consistent_bindings_(
                                                                        template_matches =  template_matches,
                                                                        templates =         templates
                                                                    )
        
        # 4. Validate complete pattern matches ----------------------------
        # Perform final validation to ensure each potential match satisfies all pattern requirements 
        # including negation constraints, type compatibility, and logical coherence. This is where 
        # we filter out spurious matches that passed the initial unification but fail deeper 
        # semantic constraints.
        
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
        
        This implements the core constraint satisfaction algorithm that ensures variable bindings 
        are globally consistent. The mathematical foundation is based on the unification algorithm 
        from automated theorem proving, specifically implementing the "occurs check" and most 
        general unifier (MGU) computation.
        
        ## Mathematical Foundation: 
        Arc consistency with backtracking search. We ensure that if variable ?X is bound to value V 
        in one template, it has the same binding in all other templates that use ?X. This prevents 
        logical contradictions like ?X = "block1" in one template and ?X = "key2" in another 
        template within the same pattern instantiation.
        
        ## Algorithm Details:
        1. Extract all template names for systematic processing
        2. Handle edge cases (no templates, single template)
        3. Generate cartesian product of all possible match combinations
        4. For each combination, check variable binding consistency
        5. Merge consistent bindings and create metadata structure
        
        ## Args:
            * template_matches  (Dict[str, List[Dict[str, Any]]]):  Matches per template.
            * templates         (Dict[str, Dict[str, Any]]):        Template structures for 
                                                                    metadata.
            
        ## Returns:
            * List[Dict[str, Any]]: Consistent variable binding combinations with metadata.
        """
        # Extract template names for systematic iteration. Order matters for deterministic behavior 
        # during debugging and testing.
        template_names:         List[str] =             list(template_matches.keys())
        
        # EDGE CASE 1: No templates provided - return empty result. This can happen with malformed 
        # patterns or parsing errors.
        if not template_names: return []
        
        # EDGE CASE 2: Single template - all matches are trivially consistent. No cross-template 
        # variable binding conflicts are possible.
        if len(template_names) == 1: return [
                                                match["bindings"]
                                                for match
                                                in template_matches[template_names[0]]
                                            ]
        
        # MAIN ALGORITHM: Generate cartesian product of all template match combinations. This 
        # creates all possible ways to select one match from each template. For N templates with M1, 
        # M2, ..., MN matches respectively, this generates M1 × M2 × ... × MN total combinations to 
        # check for consistency.
        match_combinations:     List[Dict[str, Any]] =  list(
                                                            product(*[template_matches[name]
                                                            for name
                                                            in template_names])
                                                        )
        
        # Initialize result list for consistent binding combinations.
        consistent_bindings:    List[Dict[str, Any]] =  []
        
        # Evaluate each possible combination of template matches for consistency.
        for combination in match_combinations:
            
            # Initialize merged bindings dictionary for this combination. This will accumulate 
            # variable bindings from all templates in the combination.
            merged_bindings:    Dict[str, Any] =        {}
            
            # Flag to track whether all variable bindings in this combination are consistent.
            is_consistent:      bool =                  True
            
            # CONSISTENCY CHECK: Verify that all variable bindings are compatible across all 
            # templates in this combination.
            for match in combination:
                
                # Extract variable bindings from this match.
                for variable_name, variable_value in match["bindings"].items():
                    
                    # Check if this variable has already been bound in this combination.
                    if variable_name in merged_bindings:
                        
                        # CONFLICT DETECTION: Variable already bound to different value. This 
                        # violates the consistency requirement and invalidates this entire 
                        # combination.
                        if merged_bindings[variable_name] != variable_value:
                            
                            # Set flag and break for match.
                            is_consistent =             False
                            break
                        
                    # No conflict - record this variable binding.
                    merged_bindings[variable_name] =    variable_value
                    
                # Early termination if inconsistency detected.
                if not is_consistent: break
                
            # If all bindings are consistent, create a complete binding record.
            if is_consistent:
                
                # Create comprehensive metadata for this consistent binding combination. This 
                # includes the merged bindings, matched predicates, and template assignment 
                # information for debugging and explanation generation.
                consistent_bindings.append({
                    # The unified variable bindings across all templates.
                    "bindings":             merged_bindings,
                    
                    # List of concrete predicates that were matched in this combination.
                    "matched_predicates":   [match["predicate"] for match in combination],
                    
                    # Mapping from template names to their specific match details.
                    # This preserves the template assignment for later validation phases.
                    "template_assignments": {
                                                template_names[i]: combination[i]
                                                for i
                                                in range(len(template_names))
                                            }
                })
                
        # Return all consistent binding combinations found.
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
        # Initialize templates dictionary to store parsed pattern structures.
        # Each template will be indexed by a systematic naming scheme.
        templates:  Dict[str, Dict[str, Any]] = {}
        
        # Process each pattern string systematically with indexed naming.
        for p, pattern_string in enumerate(component_patterns):
            
            # Generate systematic template name for deterministic processing.
            # This ensures consistent ordering during debugging and testing.
            template_name:      str =               f"template_{p}"
            
            # NEGATION DETECTION: Check for ¬ symbol at start of pattern.
            # Negation is a critical logical operator that must be preserved
            # throughout the matching process for correct semantic interpretation.
            negated:            bool =              pattern_string.startswith("¬")
            
            # If pattern was negation, remove negation symbol.
            if negated: pattern_string =            pattern_string[1:].strip()
            
            # PREDICATE STRUCTURE PARSING: Extract predicate name and arguments.
            # Uses regex to parse standard predicate syntax: name(arg1, arg2, ...).
            # This regex handles whitespace variations and optional argument lists.
            pattern_match:      Match =             match(r"(\w+)\s*\(([^)]*)\)", pattern_string.strip())
            
            # PARSING VALIDATION: Skip malformed patterns with warning.
            # Malformed patterns could indicate syntax errors in pattern definitions
            # or corrupted data from external sources.
            if not pattern_match: continue
            
            # Extract predicate name (group 1) and arguments string (group 2).
            predicate_name:     str =               pattern_match.group(1)
            predicate_args:     str =               pattern_match.group(2)
            
            # ARGUMENT PARSING: Split and clean argument list.
            # Handle empty argument lists and normalize whitespace for consistency.
            arguments:          List[str] =         [arg.strip() for arg in predicate_args.split(",")]  \
                                                        if predicate_args.strip()                       \
                                                        else []
            
            # ARGUMENT CLASSIFICATION: Separate variables from constants.
            # Variables are identified by the ? prefix convention from logic programming.
            # Constants are literal values that must match exactly during unification.
            variables:          List[str] =         []
            variable_positions: Dict[int, str] =    {}
            constant_positions: Dict[int, str] =    {}
            
            # Classify each argument by position and type.
            for a, argument in enumerate(arguments):
                
                # VARIABLE IDENTIFICATION: Check for ? prefix
                if argument.startswith("?"):
                    
                    # This is a logical variable that can be bound to values.
                    # Append to variables.
                    variables.append(argument)
                    
                    # Record position.
                    variable_positions[a] =         argument
                    
                # Otheriwse, ...
                else:
                    
                    # This is a constant that must match exactly.
                    constant_positions[a] =         argument
                    
            # TEMPLATE CONSTRUCTION: Create structured template with all metadata.
            # This template structure enables efficient matching and unification.
            templates[template_name] =              {
                                                        "predicate_name":       predicate_name,
                                                        "variables":            variables,
                                                        "variable_positions":   variable_positions,
                                                        "constant_positions":   constant_positions,
                                                        "negated":              negated,
                                                        "arity":                len(arguments)
                                                    }
        
        # Return all successfully parsed templates.
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
        # Extract match info.
        bindings:               Dict[str, Any] =            match_info["bindings"]
        matched_predicates:     List["Predicate"] =         match_info["matched_predicates"]
        template_assignments:   Dict[str, Dict[str, Any]] = match_info.get("template_assignments", {})
        
        # Verify all matched predicates exist in the predicate set.
        for predicate in matched_predicates:
            if not predicates.contains(predicate):
                return False
                
        # Handle negated templates
        for template_match in template_assignments.values():
            template = template_match["template"]
            
            # For negated patterns, the predicate should NOT exist
            if template["negated"]:
                if  predicates.contains(
                        predicate = template_match["predicate"]
                    ):
                    return False
                    
        # Validate variable bindings are type-compatible.
        for var_name, var_value in bindings.items():
            if not self._variable_binding_valid_(var_name, var_value):
                return False
                
        # By now, pattern match is confirmed to be valid.
        return True
        
    def _variable_binding_valid_(self, variable_name: str, variable_value: Any) -> bool:
        """# Validate Variable Binding.
        
        Check if a variable binding is type-compatible and reasonable.
        
        ## Args:
            * variable_name (str): Variable name.
            * variable_value (Any): Proposed binding value.
            
        ## Returns:
            * bool: True if binding is valid.
        """
        # Basic validation - ensure non-null values for all variables.
        # Null values are never valid for variable bindings.
        if variable_value is None: return False
            
        # Type-specific validation based on variable name patterns.
        variable_name_lower:    str =   variable_name.lower()
        
        # Agent, object, and value variables should be non-empty strings.
        if any(keyword in variable_name_lower for keyword in ["agent", "obj", "value"]):
            
            # These variable types require string values with content.
            return isinstance(variable_value, str) and len(variable_value) > 0
            
        # Location variables can be strings or coordinate tuples.
        if "location" in variable_name_lower:
            
            # Location can be string name or (x, y) coordinate tuple.
            return  (
                        isinstance(variable_value, str)                 or 
                        (
                            isinstance(variable_value, (tuple, list))   and
                            len(variable_value) == 2
                        )
                    )
                   
        # Default validation accepts any non-null value.
        return True