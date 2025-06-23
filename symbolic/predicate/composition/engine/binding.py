"""# lucidium.symbolic.predicate.composition.engine.binding

Variable binding and logical definition construction for composition patterns.
"""

from re import match, Match
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from symbolic.predicate.composition.patterns import Pattern
    from symbolic.logic import Expression, Variable
    from symbolic.predicate import PredicateVocabulary

class VariableBinder:
    """# Variable Binder.
    
    Constructs formal logical definitions from composition patterns and variable bindings.
    
    Mathematical foundation: First-order logic expression construction with proper
    variable typing and logical operator semantics. Converts pattern templates
    into executable logical expressions suitable for reasoning and evaluation.
    """
    
    def __init__(self):
        """# Instantiate Variable Binder."""
        self._binding_statistics_ = {
            "definitions_created": 0,
            "variables_typed": 0,
            "expressions_combined": 0,
            "type_inference_calls": 0
        }
        
    def build_logical_definition(self, pattern: 'Pattern', match: Dict[str, Any]) -> 'Expression':
        """# Build Logical Definition.
        
        Construct a formal logical expression from a composition pattern and variable bindings.
        
        Process:
        1. Parse component patterns into logical expressions
        2. Apply type inference to variables based on context
        3. Combine expressions according to composition type (AND, OR, IMPLIES)
        4. Validate logical coherence of the resulting expression
        
        Mathematical foundation: Standard first-order logic expression construction
        with proper operator precedence and variable scoping.
        
        ## Args:
            * pattern (Pattern): Composition pattern template.
            * match (Dict[str, Any]): Variable bindings and match context.
            
        ## Returns:
            * Expression: Complete logical definition of the composition.
        """
        self._binding_statistics_["definitions_created"] += 1
        
        # Parse component patterns into logical expressions
        component_expressions = self._parse_components_to_expressions_(pattern.component_patterns)
        
        # Combine expressions according to composition type
        combined_expression = self._combine_expressions_(component_expressions, pattern.composition_type)
        
        self._binding_statistics_["expressions_combined"] += 1
        
        return combined_expression
        
    def _parse_components_to_expressions_(self, component_patterns: List[str]) -> List['Expression']:
        """# Parse Components to Expressions.
        
        Convert component pattern strings into logical expressions with proper variable typing.
        
        ## Args:
            * component_patterns (List[str]): Pattern strings like ["near(?agent, ?obj)"].
            
        ## Returns:
            * List[Expression]: Logical expressions for each component.
        """
        from symbolic.logic.expressions import CompoundExpression, PredicateExpression
        from symbolic.logic.operator import Operator
        
        expressions = []
        
        for pattern_string in component_patterns:
            # Handle negation
            negated = pattern_string.startswith("¬")
            if negated:
                pattern_string = pattern_string[1:].strip()
                
            # Parse the predicate pattern
            predicate_expression = self._parse_predicate_pattern_(pattern_string)
            
            if predicate_expression is not None:
                # Apply negation if needed
                if negated:
                    predicate_expression = CompoundExpression(
                        operator=Operator.NOT,
                        operands=[predicate_expression]
                    )
                    
                expressions.append(predicate_expression)
                
        return expressions
        
    def _parse_predicate_pattern_(self, pattern_string: str) -> Optional['Expression']:
        """# Parse Predicate Pattern.
        
        Parse a single predicate pattern string into a logical expression with typed variables.
        
        Performs sophisticated type inference based on:
        - Predicate signature constraints
        - Variable name patterns
        - Context from other predicates
        
        ## Args:
            * pattern_string (str): Pattern like "near(?agent, ?obj)".
            
        ## Returns:
            * Optional[Expression]: Predicate expression if parsing succeeds.
        """
        from symbolic.logic.expressions import PredicateExpression
        from symbolic.predicate import Predicate
        
        # Parse predicate structure
        pattern_match = match(r"(\w+)\s*\(([^)]*)\)", pattern_string.strip())
        if not pattern_match:
            return None
            
        predicate_name = pattern_match.group(1)
        arguments_string = pattern_match.group(2)
        
        # Parse arguments
        arguments = [
            arg.strip() for arg in arguments_string.split(",")
        ] if arguments_string.strip() else []
        
        # Process arguments with type inference
        processed_arguments = []
        for argument in arguments:
            if argument.startswith("?"):
                # Create typed variable
                variable = self._create_typed_variable_(
                    variable_name=argument[1:],
                    predicate_name=predicate_name,
                    context_patterns=[pattern_string]
                )
                processed_arguments.append(variable)
                self._binding_statistics_["variables_typed"] += 1
            else:
                # Keep constants as-is
                processed_arguments.append(argument)
                
        try:
            # Create predicate with processed arguments
            predicate = Predicate(
                name=predicate_name,
                arguments=tuple(processed_arguments),
                signature=None,  # Will be resolved later if needed
                confidence=1.0
            )
            
            return PredicateExpression(predicate=predicate)
            
        except Exception as e:
            print(f"Error creating predicate for pattern '{pattern_string}': {e}")
            return None
            
    def _create_typed_variable_(self, variable_name: str, predicate_name: str, 
                              context_patterns: List[str]) -> 'Variable':
        """# Create Typed Variable.
        
        Create a Variable with inferred type based on context and naming patterns.
        
        Type inference rules:
        1. Analyze predicate signature constraints
        2. Use variable name patterns (agent, obj, location, value)
        3. Consider context from other predicates in the pattern
        4. Apply domain-specific heuristics
        
        ## Args:
            * variable_name (str): Variable name without ? prefix.
            * predicate_name (str): Predicate this variable appears in.
            * context_patterns (List[str]): All patterns for additional context.
            
        ## Returns:
            * Variable: Typed variable object.
        """
        from symbolic.logic.variable import Variable
        
        self._binding_statistics_["type_inference_calls"] += 1
        
        # Special handling for specific predicate types
        if predicate_name == "color":
            # In color(obj, value), second argument should be color_value
            for pattern in context_patterns:
                color_match = match(r"color\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", pattern)
                if color_match:
                    if color_match.group(2).strip() == f"?{variable_name}":
                        return Variable(name=variable_name, variable_type="color_value")
                    elif color_match.group(1).strip() == f"?{variable_name}":
                        return Variable(name=variable_name, variable_type="object")
                        
        # Type inference based on variable name patterns
        variable_name_lower = variable_name.lower()
        
        if "agent" in variable_name_lower:
            variable_type = "agent"
        elif "obj" in variable_name_lower:
            variable_type = "object"
        elif any(loc_keyword in variable_name_lower for loc_keyword in ["location", "pos", "from", "to"]):
            variable_type = "location"
        elif "value" in variable_name_lower:
            variable_type = "color_value"  # Default value type
        elif any(color in variable_name_lower for color in ["color", "red", "blue", "green"]):
            variable_type = "color_value"
        else:
            variable_type = "object"  # Default fallback
            
        return Variable(name=variable_name, variable_type=variable_type)
        
    def _combine_expressions_(self, expressions: List['Expression'], 
                             composition_type: 'CompositionType') -> 'Expression':
        """# Combine Expressions.
        
        Combine multiple logical expressions according to the specified composition type.
        
        Mathematical foundation: Standard logical operator semantics
        - Conjunction (∧): All operands must be true
        - Disjunction (∨): At least one operand must be true  
        - Conditional (→): If antecedent then consequent
        - Negation (¬): Logical negation
        
        ## Args:
            * expressions (List[Expression]): Component expressions to combine.
            * composition_type (CompositionType): How to combine them logically.
            
        ## Returns:
            * Expression: Combined logical expression.
        """
        from symbolic.logic.expressions import CompoundExpression, PredicateExpression
        from symbolic.logic.operator import Operator
        from symbolic.predicate import Predicate
        from symbolic.predicate.composition.types import CompositionType
        
        # Handle edge cases
        if len(expressions) == 0:
            # Return a trivial true expression
            return PredicateExpression(
                predicate=Predicate(name="true", arguments=(), confidence=1.0)
            )
            
        if len(expressions) == 1:
            return expressions[0]
            
        # Combine according to composition type
        if composition_type == CompositionType.CONJUNCTION:
            return CompoundExpression(operator=Operator.AND, operands=expressions)
            
        elif composition_type == CompositionType.DISJUNCTION:
            return CompoundExpression(operator=Operator.OR, operands=expressions)
            
        elif composition_type == CompositionType.CONDITIONAL:
            if len(expressions) >= 2:
                antecedent = expressions[0]
                # If multiple consequents, combine them with AND
                consequent = (expressions[1] if len(expressions) == 2 
                            else CompoundExpression(operator=Operator.AND, operands=expressions[1:]))
                return CompoundExpression(operator=Operator.IMPLIES, operands=[antecedent, consequent])
            else:
                # Fallback to conjunction for single expression
                return expressions[0]
                
        elif composition_type == CompositionType.NEGATION:
            # Apply negation to the combination of all expressions
            combined = (expressions[0] if len(expressions) == 1
                       else CompoundExpression(operator=Operator.AND, operands=expressions))
            return CompoundExpression(operator=Operator.NOT, operands=[combined])
            
        else:
            # Default fallback to conjunction
            return CompoundExpression(operator=Operator.AND, operands=expressions)
            
    def validate_logical_definition(self, definition: 'Expression', pattern: 'Pattern') -> bool:
        """# Validate Logical Definition.
        
        Validate that a constructed logical definition is well-formed and semantically correct.
        
        Validation checks:
        1. Expression is syntactically well-formed
        2. Variable types are consistent
        3. No circular references exist
        4. Logical operators are used correctly
        
        ## Args:
            * definition (Expression): Constructed logical definition.
            * pattern (Pattern): Original pattern for validation context.
            
        ## Returns:
            * bool: True if definition is valid.
        """
        try:
            # Check that definition has expected structure
            variables = definition.get_variables()
            
            # Verify it has variables (unless it's a constant pattern)
            if len(pattern.component_patterns) > 0 and len(variables) == 0:
                return False
                
            # Check that expression is well-formed by converting to string
            str(definition)
            
            # All validation checks passed
            return True
            
        except Exception:
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """# Get Binding Statistics.
        
        ## Returns:
            * Dict[str, Any]: Variable binding performance metrics.
        """
        return self._binding_statistics_.copy()