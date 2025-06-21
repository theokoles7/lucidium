"""# lucidium.symbolic.composition.CompositionEngine

Define engine for discovering and creating composite predicates.
"""

from itertools                          import product
from re                                 import findall, match, Match
from typing                             import Any, Dict, List, Optional, Set, Tuple

from symbolic.composition.candidate     import Candidate
from symbolic.composition.pattern       import Pattern
from symbolic.composition.signature     import CompositePredicateSignature
from symbolic.composition.type          import CompositionType
from symbolic.composition.validation    import Validator
from symbolic.logic                     import CompoundExpression, Expression, Operator, PredicateExpression, Variable
from symbolic.predicate                 import Predicate, PredicateCategory, PredicateSet, PredicateSignature, PredicateVocabulary

class CompositionEngine():
    """# Composition Engine.
    
    Main engine for discovering and creating composite predicates.
    
    This is the central orchestrator for the hierarchical predicate discovery process. It manages:
        1. Collection of composition candidates from experience
        2. Statistical evaluation of candidates
        3. Validation and promotion of candidates to actual predicates
        4. Maintenance of the predicate hierarchy
    
    The engine operates in cycles:
        1. Analyze recent experience data for patterns
        2. Update statistics for existing candidates
        3. Create new candidates for novel patterns
        4. Validate and promote ready candidates
        5. Update the predicate vocabulary and hierarchy
    """
    
    def __init__(self,
        vocabulary:                 PredicateVocabulary,
        maximum_composition_depth:  int =                   5,
        minimum_utility_threshold:  float =                 0.1
    ):
        """# Instantiate Composition Engine.

        ## Args:
            * vocabulary                (PredicateVocabulary):  Vocabulary for verification of 
                                                                predicates.
            * maximum_composition_depth (int, optional):        Maximum depth at which verification 
                                                                will cease to prevent overly complex 
                                                                hierarchies.
            * minimum_utility_threshold (int, optional):        Minimum utility that compositions 
                                                                must demonstrate to qualify as 
                                                                worthwhile.
        """
        # Define vocabulary.
        self._vocabulary_:  PredicateVocabulary =   vocabulary
        
        # Initialize validator.
        self._validator_:   Validator =             Validator(
                                                        vocabulary =                vocabulary,
                                                        maximum_composition_depth = maximum_composition_depth,
                                                        minimum_utility_threshold = minimum_utility_threshold
                                                    )
        
        # Initialize candidates map.
        self._candidates_:  Dict[str, Candidate] =  {}
        
        # Initialize list of patters.
        self._patterns_:    List[Pattern] =         []
        
        # Initialize statistics.
        self._statistics_:  Dict[str, Any] =        {
                                                        "total_candidates_created":     0,
                                                        "total_compositions_promoted":  0,
                                                        "average_discovery_time":       0.0
                                                    }
        
        # Initialize with common composition patterns.
        self._initialize_common_patterns_()
        
    def _build_logical_definition_(self,
        pattern:    Pattern,
        match:      Dict[str, Any]
    ) -> Expression:
        """# Build Logical Definition.
    
        Build a logical definition from a composition pattern and variable bindings.
        
        This creates the formal logical expression that represents the discovered composition. 
        
        ## Examples:
        - Pattern: ["near(?agent, ?obj)", "color(?obj, red)"]  
        - Result: AND(near(?agent, ?obj), color(?obj, red))

        ## Args:
            * pattern   (Pattern):          Composition pattern.
            * match     (Dict[str, Any]):   Variable bindings and match information.

        ## Returns:
            * Expression:   Complete logical definition of composition.
        """
        # Combine expressions according to composition type.
        return  self._combine_expressions_(
                    # Parse component patterns into logical expressions.
                    expressions =       self._parse_components_to_expressions_(
                                            component_patterns =    pattern.component_patterns
                                        ),
                    composition_type =  pattern.composition_type
                )

    def _calculate_binding_diversity_(self,
        candidate:  Candidate
    ) -> float:
        """# Calculate Binding Diversity.
        
        Measure the diversity of variable bindings for this pattern. More diverse bindings indicate 
        a more general and useful pattern.
        
        ## Args:
            * candidate (Candidate):    Candidate to analyze
        
        ## Returns:
            * float:    Diversity score between 0.0 and 1.0
        """
        # Analyze the diversity of variable bindings across instances.
        all_instances:          List[Dict[str, Any]] =  (
                                                            candidate.positive_instances + 
                                                            candidate.negative_instances
                                                        )
        
        # Need multiple instances to measure diversity.
        if len(all_instances) <= 1: return 0.0
        
        # Collect all unique binding combinations.
        unique_binding_sets:    Set[str] =              set()
        
        for instance in all_instances:
            # Extract bindings from the instance.
            bindings: Dict[str, Any] = instance.get('match', {}).get('bindings', {})
            
            # Create a canonical string representation.
            unique_binding_sets.add("_".join(
                f"{k}:{v}" for k, v in sorted(bindings.items())
            ))
        
        # Diversity is the ratio of unique bindings to total instances.
        # Higher diversity means the pattern generalizes across different objects.
        return len(unique_binding_sets) / len(all_instances)
        
    def _calculate_co_occurence_(self,
        candidate:  Candidate
    ) -> float:
        """# Calculate Co-Occurence.
    
        Calculate how often the component predicates co-occur together.
        
        This measures the statistical strength of the pattern by analyzing how frequently the 
        component predicates appear together compared to their individual appearance rates.

        ## Args:
            * candidate (Candidate):    Candidate whose co-occurence is being calculated.

        ## Returns:
            * float:    Co-occurrence score between 0.0 and 1.0
                * 1.0:  Predicates always appear together when pattern is relevant
                * 0.5:  Random co-occurrence
                * 0.0:  Predicates never appear together
        """
        # Get all instances where this pattern was observed.
        all_instances:          List[Dict[str, Any]] =  candidate.positive_instances + \
                                                        candidate.negative_instances
        
        # If there are no instances, there is no co-occurrence.
        if len(all_instances) == 0: return 0.0
        
        # Count how many instances have all required predicates present.
        complete_pattern_count: int =                   0
        
        # For each instance provided...
        for instance in all_instances:
            
            # Check if all expected predicates are present in this instance.
            matched_predicates:     List[Predicate] =   instance.get('matched_predicates', [])
            expected_components:    int =               len(candidate.pattern.component_patterns)
            
            # If all pattern components were matched, count as complete.
            if len(matched_predicates) >= expected_components: complete_pattern_count += 1
        
        # Co-occurrence is the ratio of complete patterns to total observations.
        return complete_pattern_count / len(all_instances)
    
    def _calculate_distinctiveness_(self,
        candidate:  Candidate
    ) -> float:
        """# Calculate Distinctiveness.
    
        Calculate how distinctive/unique this composition is compared to existing knowledge.
        
        Distinctiveness measures how much new information this pattern provides:
            * High distinctiveness: Pattern captures something unique and valuable.
            * Low distinctiveness: Pattern is redundant with existing knowledge.

        ## Args:
            * candidate (Candidate):    Candidate whose distinctiveness is being calculated.

        ## Returns:
            * float:    Distinctiveness score between 0.0 and 1.0
                * 1.0: Highly distinctive and novel
                * 0.5: Moderately distinctive  
                * 0.0: Completely redundant
        """
        # Factor 1: Pattern complexity (more complex = potentially more distinctive)
        pattern_complexity:     float = self._calculate_pattern_complexity_(
                                            candidate = candidate
                                        )
        
        # Factor 2: Binding diversity (more diverse bindings = more general pattern)
        binding_diversity:      float = self._calculate_binding_diversity_(
                                            candidate = candidate
                                        )
        
        # Factor 3: Predictive power (better than random = more distinctive)
        predictive_power:       float = max(0.0, candidate.confidence - 0.5) * 2.0  # Normalize to 0-1
        
        # Combine factors with equal weights
        return (pattern_complexity + binding_diversity + predictive_power) / 3.0
    
    def _calculate_pattern_complexity_(self,
        candidate:  Candidate
    ) -> float:
        """# Calculate Pattern Complexity.
    
        Measure the complexity of the pattern structure.
        
        ## Args:
            * candidate (Candidate):    Candidate to analyze
        
        ## Returns:
            * float:    Complexity score between 0.0 and 1.0
        """
        # Count number of component patterns.
        num_components:         int =       len(candidate.pattern.component_patterns)
        
        # Count unique variables across all components.
        unique_variables:       Set[str] =  set()
        
        # For each component...
        for component in candidate.pattern.component_patterns:
            
            # Extract variables from component pattern string.
            unique_variables.update(findall(r'\?(\w+)', component))
        
        # Record number of variables.
        num_variables:          int =       len(unique_variables)
        
        # Complexity increases with more components and variables.
        # Normalize to 0-1 range (assuming reasonable maximums).
        component_complexity:   float =     min(1.0, num_components / 3.0)
        variable_complexity:    float =     min(1.0, num_variables / 5.0)
        
        # Average the complexities
        return (component_complexity + variable_complexity) / 2.0
    
    def _combine_expressions_(self,
        expressions:        List[Expression],
        composition_type:   CompositionType
    ) -> Expression:
        """# Combine Expressions.
    
        Combine multiple expressions according to the composition type.

        ## Args:
            * expressions       (List[Expression]): Component expressions to combine.
            * composition_type  (CompositionType):  How to combine them (AND, OR, etc.)

        ## Returns:
            * Expression:   Combined logical expression.
        """
        # If no expressions were provided, return a simple truth expression.
        if len(expressions) == 0:               return  PredicateExpression(
                                                            predicate = Predicate(
                                                                            name =          "true",
                                                                            arguments =     (),
                                                                            confidence =    1.0
                                                                        )
                                                        )
        
        # If only one expression was provided, simply return that expression.
        if len(expressions) == 1:               return  expressions[0]
        
        # Otherwise, match composition type.
        match composition_type:
            
            # Conjunction.
            case CompositionType.CONJUNCTION:   return  CompoundExpression(
                                                            operator =  Operator.AND,
                                                            operands =  expressions
                                                        )
            
            # Disjunction.
            case CompositionType.DISJUNCTION:   return  CompoundExpression(
                                                            operator =  Operator.OR,
                                                            operands =  expressions
                                                        )
            
            # Conditional.
            case CompositionType.CONDITIONAL:
                
                # Ensure that at least two operands are provided.
                if len(expressions) >= 2:       return  CompoundExpression(
                                                            operator =  Operator.IMPLIES,
                                                            operands =  [
                                                                            # Antecedent.
                                                                            expressions[0],
                                                                            
                                                                            # Consequent.
                                                                            expressions[1]
                                                                                if len(expressions) == 2
                                                                                else    CompoundExpression(
                                                                                            operator =  Operator.AND,
                                                                                            operands =  expressions[1:]
                                                                                )
                                                                        ]
                                                        )
                
            # Default will be conjunction.
            case _:                             return  CompoundExpression(
                                                            operator =  Operator.AND,
                                                            operands =  expressions
                                                        )
    
    def _create_predicate_(self,
        candidate:  Candidate
    ) -> None:
        """# Create Candidate.
        
        Create and register a new composite predicate from a validated candidate.

        ## Args:
            * candidate (Candidate):    The validated composition candidate.
        """
        # Try to add predicate to vocabulary.
        if  self._vocabulary_.add_signature(
                signature = CompositePredicateSignature(
                    name =                  candidate.pattern.result_signature.name,
                    argument_types =        candidate.pattern.result_signature.arg_types,
                    component_predicates =  [],
                    definition =            candidate.definition,
                    category =              PredicateCategory.COMPOSITE,
                    description =           candidate.pattern.description
                )
            ):
            
            # Report success.
            print(f"Created new composite predicate.")
            
        # Otherwise, report failure.
        else: print(f"Failed to add composite predicate.")
        
    def _create_new_candidate_(self,
        pattern:    Pattern,
        match:      Dict[str, Any]
    ) -> None:
        """# Create New Candidate.
    
        Create a new composition candidate with proper logical definition.
        
        This method constructs the logical definition by:
            1. Parsing the component patterns from the composition pattern
            2. Creating logical expressions for each component
            3. Combining them according to the composition type (AND, OR, etc.)
            4. Creating a candidate with the complete logical definition

        ## Args:
            * pattern   (Pattern):          Composition pattern that matched.
            * match     (Dict[str, Any]):   Variable bindings for the match.
        """
        # Create proper logical definition based on pattern and match.
        definition:         Expression =            self._build_logical_definition_(
                                                        pattern =       pattern,
                                                        match =         match
                                                    )
        
        # Create candidate.
        candidate:          Candidate =             Candidate(
                                                        pattern =       pattern,
                                                        definition =    definition
                                                    )
        
        # Extract key for storing candidate.
        candidate_key:      str =                   self._get_candidate_key_(
                                                        pattern =       pattern,
                                                        match =         match
                                                    )
        
        # Add candidate to list.
        self._candidates_[candidate_key] =          candidate
        
        # Update discovery statistics.
        self._statistics_['total_candidates_created'] += 1
        
    def _create_variable_with_type_inference_(self,
        variable_name:      str,
        context_patterns:   List[str]
    ) -> Variable:
        """# Create Variable with Type Inference.
    
        Create a Variable object with inferred type based on context.

        ## Args:
            * variable_name     (str):          Variable name (without prefix).
            * context_patterns  (List[str]):    All patterns for context analysis.

        ## Returns:
            * Variable: Variable with appropriate type annotation.
        """
        # For each pattern provided...
        for pattern in context_patterns:
            
            # Analyze context to determine more specific types
            if f"?{variable_name}" in pattern:
                
                # Special handling for color predicate
                if "color(" in pattern:
                    
                    # Parse the color pattern to determine argument positions
                    color_match = match(r"color\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", pattern)
                    
                    # If match was found...
                    if color_match:
                        
                        # If this variable is the second argument in color(), it should be color_value
                        if color_match.group(2).strip() ==      f"?{variable_name}":   return   Variable(
                                                                                                    name =          variable_name,
                                                                                                    variable_type = "color_value"
                                                                                                )
                        
                        # If it's the first argument, it should be object
                        elif color_match.group(1).strip() ==    f"?{variable_name}":  return    Variable(
                                                                                                    name =          variable_name,
                                                                                                    variable_type = "object"
                                                                                                )
        
        # Infer type from variable name
        if      "agent"     in variable_name.lower():   variable_type:  str =   "object"
        elif    "obj"       in variable_name.lower():   variable_type:  str =   "object" 
        elif    "location"  in variable_name.lower() \
            or  "pos"       in variable_name.lower():   variable_type:  str =   "location"
        elif    "value"     in variable_name.lower():   variable_type:  str =   "color_value"  # Default to color_value for ?value
        elif    any(
                color       in variable_name.lower()
                for color
                in  [
                        "color",
                        "red",
                        "blue",
                        "green"
                    ]
                ):                                      variable_type:  str =   "color_value"
        else:                                           variable_type:  str =   "object"
        
        # Provide variable.
        return  Variable(
                    name =          variable_name,
                    variable_type = variable_type
                )
        
    def _evaluate_candidates_(self) -> None:
        """# Evaluate Candidates.
        
        Evaluate all composition candidates and update their scores.
        
        This recalculates statistical measures like confidence, support, and utility for all active 
        candidates based on accumulated evidence.
        """
        # For each candidate stored...
        for candidate_key, candidate in self._candidates_.items():
        
            # Update utility score using the candidate's own method
            candidate.calculate_utility()
            
            # Update co-occurence.
            candidate.co_occurence =        self._calculate_co_occurence_(
                                                candidate = candidate
                                            )
            
            # Update distinctiveness.
            candidate.disctinctiveness =    self._calculate_distinctiveness_(
                                                candidate = candidate
                                            )
            
    def _find_consistent_bindings_(self,
        template_matches:   Dict[str, List[Dict[str, Any]]],
        templates:          Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """# Find Consistent Bindings.
    
        Find variable binding combinations that are consistent across all templates.
        
        This uses constraint satisfaction to ensure that if variable ?X is bound to "key1" in one 
        template, it must be bound to "key1" in all other templates that use ?X.

        ## Args:
            * template_matches  (Dict[str, List[Dict[str, Any]]]):  Matches for each template.
            * templates         (Dict[str, Dict[str, Any]]):        Original template definitions.

        ## Returns:
            * List[Dict[str, Any]]: List of consistent variable binding combinations.
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
        
    def _find_pattern_matches_(self,
        pattern:    Pattern,
        predicates: PredicateSet
    ) -> List[Dict[str, Any]]:
        """# Find Pattern Matches.
        
        Find all instances where a composition pattern matches the predicates.
        
        This involves pattern matching to see if the component predicates of a composition pattern 
        are present in the current predicate set, with consistent variable bindings.
        
        ## The algorithm:
            1. Parse component patterns to extract predicate templates
            2. Find candidate predicates that match each template
            3. Use unification to find consistent variable bindings
            4. Validate that all pattern components can be satisfied simultaneously

        ## Args:
            * pattern       (CompositionPattern):   Composition pattern to match.
            * predicates    (PredicateSet):         Current predicate set.

        ## Returns:
            * List[Dict[str, Any]]: List of match dictionaries with variable bindings.
        """
        # 1: Parse component patterns into searchable templates.
        pattern_templates:      Dict[str, Dict[str, Any]] = self._parse_component_patterns_(
                                                                component_patterns =    pattern.component_patterns
                                                            )
        
        # 2: Find all possible matches for each template.
        template_matches:       Dict[str, Any] =            {
                                                                template_name:  self._find_template_matches_(
                                                                                    template =      template,
                                                                                    predicates =    predicates
                                                                                )
                                                                for template_name, template
                                                                in pattern_templates.items()
                                                            }
        
        # 3: Find consistent variable bindings across all templates.
        consistent_bindings:    List[Dict[str, Any]] =      self._find_consistent_bindings_(
                                                                template_matches =  template_matches,
                                                                templates =         pattern_templates
                                                            )
        
        # 4: Validate and return matches.
        return  [
                    bindings
                    for bindings
                    in consistent_bindings
                    if self._pattern_match_valid_(
                        pattern =       pattern,
                        match_info =    bindings,
                        predicates =    predicates
                    )
                ]
        
    def _find_template_matches_(self,
        template:   Dict[str, Any],
        predicates: PredicateSet
    ) -> List[Dict[str, Any]]:
        """# Find Template Matches.
    
        Find all predicates that match a specific template structure.

        ## Args:
            template    (Dict[str, Any]):   Parsed template to match against.
            predicates  (PredicateSet):     Set of predicates to search.

        ## Returns:
            * List[Dict[str, Any]]: List of matches with variable bindings
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
    
    def _get_candidate_key_(self,
        pattern:    Pattern,
        match:      Dict[str, Any]
    ) -> str:
        """# Get Candidate Key.

        ## Args:
            * pattern   (Pattern):          Composition pattern whos key is being fetched.
            * match     (Dict[str, Any]):   Variable bindings for this match.

        ## Returns:
            * str:  Candidate key.
        """
        return f"""{pattern.name}_{"_".join(f"{key}:{value}" for key, value in sorted(match.items()))}"""
        
    def _initialize_common_patterns_(self) -> None:
        """# Initialize Common Patterns.
        
        Initialize the engine with common composition patterns.
        
        These are general patterns that are useful across many domains:
            * Conjunctive patterns (A ∧ B)
            * Conditional patterns (A → B)
            * Negation patterns (¬A)
        
        Domain-specific patterns can be added later.
        """
        self._patterns_.extend([
            # Define conjunctive accessibility pattern.
            Pattern(
                name =                  "accessibility_conjunction",
                composition_type =      CompositionType.CONJUNCTION,
                component_patterns =    ["near(?agent, ?obj)", "color(?obj, ?value)"],
                result_signature =      PredicateSignature(
                                            name =          "accessible_object",
                                            arg_types =     ["object"],
                                            category =      PredicateCategory.COMPOSITE,
                                            description =   "Object is accessible to agent."
                                        ),
                confidence_threshold =  0.7,
                minimum_support =       3,
                description =           "Objects that are near each other and have specific properties."
            ),
                
            # Define safety pattern with negation.
            Pattern(
                name =                  "safety_with_negation",
                composition_type =      CompositionType.CONJUNCTION,
                component_patterns =    ["path(?from, ?to)", "¬dangerous(?from, ?to)"],
                result_signature =      PredicateSignature(
                                            name =          "safe_path",
                                            arg_types =     ["location", "location"],
                                            category =      PredicateCategory.COMPOSITE,
                                            description =   "Path between locations that is safe."
                                        ),
                confidence_threshold =  0.8,
                minimum_support =       2,
                description =           "Paths exist and are not dangerous."
            )
        ])
        
    def _parse_component_patterns_(self,
        component_patterns: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """# Parse Component Patterns.
    
        Parse component pattern strings into structured templates for matching.
        
        Examples:
            "near(?agent, ?obj)" -> {
                'predicate_name': 'near',
                'variables': ['?agent', '?obj'],
                'variable_positions': {0: '?agent', 1: '?obj'},
                'negated': False
            }
            "¬dangerous(?from, ?to)" -> {
                'predicate_name': 'dangerous', 
                'variables': ['?from', '?to'],
                'variable_positions': {0: '?from', 1: '?to'},
                'negated': True
            }

        ## Args:
            * component_patterns    (List[str]):    List of patterns strings to parse.

        ## Returns:
            * Dict[str, Dict[str, Any]]:    Mapping from template names to parsed templates.
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
            if negated: pattern_string =            pattern_string[1:]
            
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
    
    def _parse_components_to_expressions_(self,
        component_patterns: List[str]
    ) -> List[Expression]:
        """# Parse Component to Expressions.
    
        Convert component pattern strings into logical expressions.

        ## Args:
            * component_patterns    (List[str]):    Pattern strings like ["near(?agent, ?obj)", 
                                                    "color(?obj, red)"]

        ## Returns:
            * List[Expression]: List of logical expressions.
        """
        # Initialize list of expressions.
        expressions:    List[Expression] =  []
        
        # For each pattern provided...
        for pattern_string in component_patterns:
            
            # Set flag indicating if pattern is negation.
            negated:                bool =                  pattern_string.startswith("¬")
            
            # If pattern was negation, remove negation symbol.
            if negated: pattern_string =                    pattern_string[1:].strip()
            
            # Parse the predicate structure.
            predicate_expression:   Optional[Expression] =  self._parse_predicate_pattern_(
                                                                pattern_string =    pattern_string
                                                            )
            
            # If predicate expression was parsed...
            if predicate_expression is not None:
                
                # If negation was detected...
                if negated:
                    
                    # Apply negation.
                    predicate_expression =                  CompoundExpression(
                                                                operator =  Operator.NOT,
                                                                operands =  [predicate_expression]
                                                            )
                    
                # Add to list.
                expressions.append(predicate_expression)
        
        # Provide expressions.
        return expressions
    
    def _parse_predicate_pattern_(self,
        pattern_string: str
    ) -> Optional[Expression]:
        """# Parse Predicate Pattern.
    
        Parse a single predicate pattern string into a logical expression.
        
        ## Examples:
            * "near(?agent, ?obj)" -> PredicateExpression(near(?agent, ?obj))
            * "color(?obj, red)" -> PredicateExpression(color(?obj, red))

        ## Args:
            * pattern_string    (str):  Pattern like "near(?agent, ?obj)"

        ## Returns:
            * Optional[Expression]: Predicate expression if match is found.
        """
        # Parse predicate structure.
        pattern_match:          Optional[Match[str]] =  match(
                                                            pattern =   r"(\w+)\s*\(([^)]*)\)",
                                                            string =    pattern_string.strip()
                                                        )
        
        # If no match was found, return nothing.
        if not pattern_match: return None
        
        # Extract predicate name and argument strings.
        predicate_name:         str =                   pattern_match.group(1)
        arguments_string:       str =                   pattern_match.group(2)
        
        # Parse arguments.
        arguments:              List[str] =             [
                                                            argument.strip()
                                                            for argument
                                                            in arguments_string.split(",")
                                                        ]                           \
                                                        if arguments_string.strip() \
                                                        else []
                                                    
        # Initialize list of processed arguments.
        processed_arguments:    List[Any] =             []
        
        # For each argument...
        for argument in arguments:
            
            # If the argument starts with ?, it's a variable.
            if argument.startswith("?"):
                
                # Create variable object with proper type inference.
                processed_arguments.append(self._create_variable_with_type_inference_(
                    variable_name =     argument[1:],
                    context_patterns =  [pattern_string]
                ))
                
            # Otherwise, keep it as a constant.
            else: processed_arguments.append(argument)
            
        try:# Return predicate with processed arguments.
            return  PredicateExpression(
                        predicate = Predicate(
                                        name =          predicate_name,
                                        arguments =     tuple(processed_arguments),
                                        signature =     self._vocabulary_.get_signature(
                                                            name =  predicate_name
                                                        ),
                                        confidence =    1.0
                                    )
                    )
        
        # If an error occurs...  
        except Exception as e:
            
            # Report the error.
            print(f"""Error creating predicate for pattern "{pattern_string}": {e}""")
            
            # Return nothing.
            return None
            
    def _pattern_match_valid_(self,
        pattern:    Pattern,
        match_info: Dict[str, Any],
        predicates: PredicateSet
    ) -> bool:
        """# Pattern Match is Valid?
    
        Validate that a potential pattern match is actually valid by checking:
            1. All required predicates are present
            2. Negated predicates are properly handled
            3. Type constraints are satisfied
            4. No logical contradictions exist

        ## Args:
            * pattern       (Pattern):          Original composition pattern.
            * match_info    (Dict[str, Any]):   Match information with bindings.
            * predicates    (PredicateSet):     Current predicate set.

        ## Returns:
            * bool:
                * True:     Match is valid.
                * False:    Match is not valid.
        """
        # Extract match metadata.
        bindings:               Dict[str, Any] =            match_info["bindings"]
        matched_predicates:     List[Predicate] =           match_info["matched_predicates"]
        template_assignments:   Dict[str, Dict[str, Any]] = match_info["template_assignments"]
        
        # For each predicate...
        for predicate in matched_predicates:
            
            # Return false if it is not in predicate set.
            if not predicates.contains(predicate = predicate): return False
            
        # For each template...
        for template_name, template_match in template_assignments.items():
            
            # Extract template.
            template:   Dict[str, Any] =    template_match["template"]
            
            # If template was negation...
            if template["negated"]:
                
                # Ensure the predicate does not exist.
                if predicates.contains(
                    predicate = template_match["predicate"]
                ): return False
                
        # For each variable...
        for variable_name, variable_value in bindings.items():
            
            # Return false if it is not type-compatible and reasonable.
            if not self._variable_binding_valid_(
                variable_name =     variable_name,
                variable_value =    variable_value
            ): return False
            
        # If composition is a conjunction...
        if pattern.composition_type == CompositionType.CONJUNCTION:
            
            # Indicate that all components are satisfied.
            return len(matched_predicates) ==   len([
                                                    template
                                                    for template
                                                    in template_assignments.values()
                                                    if not template["template"]["negated"]
                                                ])
            
        # Otherwise, simply return False.
        return True
        
    def _process_experience_(self,
        experience: Dict[str, Any]
    ) -> None:
        """# Process (Single) Experience.
        
        Process a single experience for composition discovery.
        
        For each experience, we:
        1. Extract predicate co-occurrence patterns
        2. Match against known composition patterns
        3. Update statistics for existing candidates
        4. Create new candidates for novel patterns

        ## Args:
            * experience    (Dict[str, Any]):   Single experience data dictionary.
        """
        # Extract predicate set.
        predicates:             PredicateSet =          experience.get("predicates", PredicateSet())
        
        # Reference outcome.
        success:                bool =                  experience.get("success", False)
        
        # For each pattern...
        for pattern in self._patterns_:
            
            # Find matches.
            matches:            List[Dict[str, Any]] =  self._find_pattern_matches_(
                                                            pattern =       pattern,
                                                            predicates =    predicates
                                                        )
            
            # For each match found...
            for match in matches:
                
                # Get candidate key.
                candidate_key:  str =                   self._get_candidate_key_(
                                                            pattern =   pattern,
                                                            match =     match
                                                        )
                
                # If candidate's key does not already exist...
                if candidate_key not in self._candidates_:
                    
                    # Create new candidate.
                    self._create_new_candidate_(
                        pattern =   pattern,
                        match =     match
                    )
                    
                # Get candidate from list.
                candidate:      Candidate =             self._candidates_[candidate_key]
                
                # Add evidence of positive experience if successful.
                if success: candidate.add_positive_instance(
                                instance =  {
                                                "match":        match,
                                                "predicates":   predicates.to_list(),
                                                "experience":   experience
                                            }
                            )
                
                # Otherwise, add evidence of negative experience.
                else:       candidate.add_negative_instance(
                                instance =  {
                                                "match":        match,
                                                "predicates":   predicates.to_list(),
                                                "experience":   experience
                                            }
                            )
                
    def _promote_candidates_(self) -> None:
        """# Promote Candidates.
        
        Promote composition candidates that meet the criteria to actual predicates.
        
        This is where new composite predicates are actually created and added to the vocabulary, 
        enabling the agent to use them in reasoning.
        """
        # Marshal qualified candidates.
        ready_candidates:   List[Tuple[str, Candidate]] =   [
                                                                (key, candidate)
                                                                for key, candidate
                                                                in self._candidates_.items()
                                                                if candidate.meets_criteria
                                                            ]
        
        # For each qualified candidate...
        for key, candidate in ready_candidates:
            
            # Validate the candidate.
            is_valid, errors =  self._validator_.validate_composition(
                                    candidate = candidate
                                )
            
            # If the candidate is valid...
            if is_valid:
                
                # Create predicate.
                self._create_predicate_(candidate = candidate)
                
                # Remove candidate from list.
                del self._candidates_[key]
                
                # Update discovery statistics.
                self._statistics_["total_compositions_promoted"] += 1
                
            # Otherwise, log errors preventing promotion.
            else: print(f"""Candidate {key} failed validation: {errors}""")
            
    def _validate_definition_(self,
        definition: Expression,
        pattern:    Pattern
    ) -> bool:
        """# Validate Definition.

        ## Args:
            * definition    (Expression):   The created logical definition.
            * pattern       (Pattern):      Original pattern for validation.

        ## Returns:
            * bool:
                * True:     Definition is valid.
                * False:    Definition is not valid.
        """
        try:# Check that definition has the expected structure.
            variables:  Set[Variable] = definition.get_variables()
            
            # Verify it has at least some variables (unless it's a constant pattern).
            if      len(pattern.component_patterns) > 0 \
                and len(variables) == 0: return False
            
            # Check that the expression is well-formed by attempting to convert to string.
            str(definition)
            
            # All checks passed.
            return True
            
        # Should any error occur, the definition is not valid.
        except Exception: return False
            
    def _variable_binding_valid_(self,
        variable_name:  str,
        variable_value: Any
    ) -> bool:
        """# Variable Binding Valid?
    
        Validate that a variable binding is type-compatible and reasonable.

        ## Args:
            * variable_name     (str):  Name of variable.
            * variable_value    (Any):  Value being bound to the variable.

        ## Returns:
            * bool:
                * True:     Binding is valid.
                * False:    Binding is not valid.
        """
        # If variable is for...
        if  any([
                # Agents...
                "agent" in variable_name.lower(),
                
                # Objects...
                "obj"   in variable_name.lower(),
                
                # Or Values...
                "value" in variable_name.lower()
            ]): 
                # They should simply be non-empty strings.
                return isinstance(variable_value, str) and len(variable_value) > 0
            
        # Locations...
        if "location"   in variable_name.lower():
            
            # They should be...
            return  any([
                        # Strings...
                        isinstance(variable_value, str),
                        
                        # Or...
                        all([
                            # Tuples...
                            isinstance(variable_value, tuple),
                            
                            # With exactly two elements.
                            len(variable_value) == 2
                        ])
                    ])
            
        # Otherwise, default requirement is that the value is not None.
        return variable_value is not None
        
    def analyze_experiences(self,
        experience_data:    List[Dict[str, Any]]
    ) -> None:
        """# Analyze Experiences (Batch).
        
        Analyze a batch of experience data for composition opportunities.
        
        This is the main entry point for the discovery process. The agent calls this method 
        periodically with recent experience data, and the engine updates its candidate compositions 
        based on observed patterns.

        ## Args:
            * experience_data   (List[Dict[str, Any]]): List of experience dictionaries, each 
                                                        containing:
                * "predicates": PredicateSet from the experience
                * "actions":    Actions taken
                * "outcomes":   Results yielded
                * "success":    Whether episode was successful or not
        """
        # Process each experience provided.
        for experience in experience_data: self._process_experience_(experience)
        
        # Evaluate candidates.
        self._evaluate_candidates_()
        
        # Promote sufficient candidates.
        self._promote_candidates_()
    
    def get_statistics(self) -> Dict[str, Any]:
        """# Get Statistics.
        
        Get statistics about the composition discovery process.

        ## Returns:
            * Dict[str, Any]:   Dictionary with discovery statistics and metrics.
        """
        return  {
                    "active_candidates":    len(self._candidates_),
                    "total_patterns":       len(self._patterns_),
                    "discovery_stats":      self._statistics_.copy(),
                    "candidate_details":    {
                                                key:    {
                                                            "support":      candidate.support,
                                                            "confidence":   candidate.confidence,
                                                            "utility":      candidate.utility
                                                        }
                                                for key, candidate in self._candidates_.items()
                                            }
                }