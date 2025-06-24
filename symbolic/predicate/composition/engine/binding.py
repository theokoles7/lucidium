"""# lucidium.symbolic.predicate.composition.Binder

Variable binding and logical definition construction for composition patterns.
"""

__all__ = ["VariableBinder"]

# Native imports
from re import match, Match
from typing                                     import Any, Dict, List, Optional, TYPE_CHECKING

# Custom imports
if TYPE_CHECKING:
    from symbolic.logic                         import Expression, Variable
    from symbolic.predicate                     import Predicate
    from symbolic.predicate.composition.pattern import Pattern
    from symbolic.predicate.composition.type    import CompositionType
    
class Binder():
    """# (Variable) Binder.
    
    Constructs formal logical definitions from composition patterns and variable bindings.
    
    Mathematical foundation: First-order logic expression construction with proper variable typing 
    and logical operator semantics. Converts pattern templates into executable logical expressions 
    suitable for reasoning and evaluation.
    """
    
    def __init__(self):
        """# Instantiate (Variable) Binder."""
        # Initialize statistics tracking for binding performance monitoring.
        self._statistics_:  Dict[str, int] =    {
                                                    # Total logical definitions constructed.
                                                    "definitions_created":  0,
                                                    
                                                    # Variables with inferred types.
                                                    "variables_typed":      0,
                                                    
                                                    # Expression combination operations
                                                    "expressions_combined": 0,
                                                    
                                                    # Type inference algorithm invocations.
                                                    "type_inference_calls": 0
                                                }
    
    # PROPERTIES ===================================================================================
    
    @property
    def statistics(self) -> Dict[str, int]:
        """# Statistics.

        Variable binding performance metrics.
        """
        return self._statistics_.copy()
        
    # METHODS ======================================================================================
    
    def build_definition(self,
        pattern:    "Pattern",
        match:      Dict[str, Any]
    ) -> "Expression":
        """# Build Logical Definition.
        
        Construct a formal logical expression from a composition pattern and variable bindings.
        
        This is the core method that transforms discovered patterns into executable logical 
        expressions suitable for reasoning and evaluation. The process implements standard 
        first-order logic construction with sophisticated type inference and operator semantics.
        
        ## Args:
            * pattern   (Pattern):          Composition pattern template containing component patterns.
            * match     (Dict[str, Any]):   Variable bindings and match context from unification.
            
        ## Returns:
            * Expression: Complete logical definition ready for reasoning and evaluation.
        """
        # Update statistics for performance monitoring and analysis.
        self._binding_statistics_["definitions_created"] +=     1
        
        # STEP 1: Parse component patterns into logical expressions.
        # Transform each component pattern string into a formal logical expression.
        component_expressions:  List["Expression"] =    self._parse_components_to_expressions_(
                                                            component_patterns =    pattern.component_patterns
                                                        )
        
        # STEP 2: Combine expressions according to composition type.
        # Apply the appropriate logical operator based on the pattern's composition type.
        combined_expression:    "Expression" =          self._combine_expressions_(
                                                            expressions =           component_expressions, 
                                                            composition_type =      pattern.composition_type
                                                        )
        
        # Update statistics for expression combination tracking.
        self._binding_statistics_["expressions_combined"] +=    1
        
        # Return the complete logical definition ready for use in reasoning.
        return combined_expression
        
    def validate_logical_definition(self, 
        definition: "Expression", 
        pattern:    "Pattern"
    ) -> bool:
        """# Validate Logical Definition.
        
        Validate that a constructed logical definition is well-formed and semantically correct.
        
        ## Args:
            * definition    (Expression):   Constructed logical definition.
            * pattern       (Pattern):      Original pattern for validation context.
            
        ## Returns:
            * bool: True if definition is valid.
        """
        try:# Check that definition has expected structure for validity.
            variables: set = definition.get_variables()
            
            # Verify it has variables unless it's a constant pattern.
            if  len(pattern.component_patterns) > 0 and \
                len(variables) == 0:
                    
                # Non-empty pattern should have at least one variable.
                return False
                
            # Check that expression is well-formed by converting to string.
            str(definition)
            
            # All validation checks passed successfully.
            return True
        
        # Any exception during validation indicates invalid definition.  
        except Exception: return False
    
    
    # HELPERS ======================================================================================
    
    def _combine_expressions_(self, 
        expressions:        List["Expression"], 
        composition_type:   "CompositionType"
    ) -> "Expression":
        """# Combine Expressions.
        
        Combine multiple logical expressions according to the specified composition type.
        
        ## Args:
            * expressions       (List[Expression]): Component expressions to combine.
            * composition_type  (CompositionType):  How to combine them logically.
            
        ## Returns:
            * Expression:   Combined logical expression.
        """
        # Import required classes for expression construction.
        from symbolic.logic.expressions             import CompoundExpression, PredicateExpression
        from symbolic.logic.operator                import Operator
        from symbolic.predicate                     import Predicate
        from symbolic.predicate.composition.type    import CompositionType
        
        # Handle edge case of no expressions provided.
        if len(expressions) == 0:
            
            # Return a trivial true expression for empty expression lists.
            return PredicateExpression(
                predicate = Predicate(name="true", arguments=(), confidence=1.0)
            )
            
        # Handle edge case of single expression provided.
        # Single expression needs no combination operator.
        if len(expressions) == 1:                               return expressions[0]
            
        # Combine expressions according to specified composition type.
            # Conjunction requires all component predicates to be true.
        if composition_type == CompositionType.CONJUNCTION:     return  CompoundExpression(
                                                                            operator =  Operator.AND,
                                                                            operands =  expressions
                                                                        )
            
        # Disjunction requires at least one component predicate to be true.
        elif composition_type == CompositionType.DISJUNCTION:   return  CompoundExpression(
                                                                            operator =  Operator.OR,
                                                                            operands =  expressions
                                                                        )
        
        # Conditoinal expressions.
        elif composition_type == CompositionType.CONDITIONAL:
            
            # Conditional creates if-then relationship between components.
            if len(expressions) >= 2:
                
                # Extract antecedent as first expression.
                antecedent: "Expression" =  expressions[0]
                
                # Create consequent from remaining expressions.
                consequent: "Expression" =  (
                                                expressions[1] 
                                                if len(expressions) == 2 
                                                else    CompoundExpression(
                                                            operator =  Operator.AND,
                                                            operands =  expressions[1:]
                                                        )
                                            )
                
                # Return implication with antecedent and consequent.
                return  CompoundExpression(
                            operator =  Operator.IMPLIES, 
                            operands =  [antecedent, consequent]
                        )
            
            # Fallback to single expression for insufficient expressions.
            else: return expressions[0]
                
        # Negation expressions.
        elif composition_type == CompositionType.NEGATION:
            
            # Apply negation to the combination of all expressions.
            combined:   "Expression" =  (
                                            expressions[0] 
                                            if len(expressions) == 1
                                            else    CompoundExpression(
                                                        operator =  Operator.AND,
                                                        operands =  expressions
                                                    )
                                        )
            
            # Return negated expression.
            return  CompoundExpression(
                        operator =  Operator.NOT,
                        operands =  [combined]
                    )
            
        # Default fallback to conjunction for unknown composition types.   
        else:   return  CompoundExpression(
                            operator =  Operator.AND,
                            operands =  expressions
                        )
        
    def _create_typed_variable_(self,
        variable_name:      str,
        predicate_name:     str,
        context_patterns:   List[str]
    ) -> "Variable":
        """# Create Typed Variable.

        ## Args:
            * variable_name     (str):          Variable name without ? prefix for analysis.
            * predicate_name    (str):          Predicate that this variable appears in for context.
            * context_patterns  (List[str]):    All patterns for additional context analysis.

        ## Returns:
            * Variable: Typed variable object with inferred type annotation.
        """
        # Update statistics for type inference performance tracking.
        self._binding_statistics_["type_inference_calls"] += 1
        
        # STRATEGY 1: Predicate-specific type inference -------------------
        
        # Use known predicate semantics to infer precise variable types.
        if predicate_name == "color":
            
            # Special handling for color predicate: color(object, color_value)
            for pattern in context_patterns:
                
                # Parse color predicate structure to determine argument positions.
                color_match:    Optional[Match[str]] =  match(
                                                            r"color\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", 
                                                            pattern
                                                        )
                
                
                if color_match:
                    # Check if this variable is the second argument (color value).
                    if color_match.group(2).strip() == f"?{variable_name}":
                        # Second argument should be color value type.
                        return Variable(name=variable_name, variable_type="color_value")
                    # Check if this variable is the first argument (object being colored).
                    elif color_match.group(1).strip() == f"?{variable_name}":
                        # First argument should be object type.
                        return Variable(name=variable_name, variable_type="object")
                        
        # STRATEGY 2: Variable name pattern analysis ----------------------
        
        # Apply heuristic rules based on common variable naming conventions.
        variable_name_lower: str = variable_name.lower()
        
        # Agent-related variables: Variables representing agents or actors.
        if "agent" in variable_name_lower:
            # Variables containing "agent" should be agent type.
            variable_type: str = "agent"
            
        # Object-related variables: General objects in the environment.
        elif "obj" in variable_name_lower:
            # Variables containing "obj" should be object type.
            variable_type = "object"
            
        # Location-related variables: Spatial positions and coordinates.
        elif any(loc_keyword in variable_name_lower for loc_keyword in [
            "location", "pos", "from", "to"
        ]):
            # Spatial keywords indicate location type.
            variable_type = "location"
            
        # Value-related variables: Generic attribute values with context-dependent typing.
        elif "value" in variable_name_lower:
            # Default value variables to color_value unless context suggests otherwise.
            variable_type = "color_value"
            
        # Color-specific variables: Explicitly color-related variable names.
        elif any(color in variable_name_lower for color in ["color", "red", "blue", "green"]):
            # Color keywords indicate color_value type.
            variable_type = "color_value"
            
        # STRATEGY 3: Default fallback for unknown patterns ========================
        else:
            # Default to "object" type for maximum compatibility with predicates.
            variable_type = "object"
            
        # Create and return the typed variable with inferred type annotation.
        return Variable(name=variable_name, variable_type=variable_type)