"""# lucidium.symbolic.predicate.PredicateSignature

Define structure and constraints of a predicate.
"""

__all__ = ["PredicateSignature"]

from dataclasses                    import dataclass
from re                             import match
from typing                         import Any, Dict, List, Set

from symbolic.predicate.category    import PredicateCategory
from symbolic.predicate.type        import PredicateType

@dataclass(frozen = True)
class PredicateSignature():
    """# Predicate Signature.
    
    Defines the structure and constraints of a predicate.
    
    ## Examples:
        * color(object, color_value) -> PredicateSignature("color", ["object", "color_value"])
        * near(object1, object2) -> PredicateSignature("near", ["object", "object"])
    """
    # Define parameters.
    name:           str
    arg_types:      List[str]
    category:       PredicateCategory = PredicateCategory.ATTRIBUTE
    description:    str =               ""
    
    def _is_valid_agent_(self,
        argument:   Any
    ) -> bool:
        """# Is Agent Valid?
        
        Check if argument is a valid agent identifier.
        
        Agents are special objects that can take actions in the environment.
        Examples: "agent", "robot1", "player", "ai_agent"

        ## Args:
            * argument  (Any):  Argument being validated.

        ## Returns:
            * bool:
                * True:     Argument is a valid agent identifier.
                * False:    Argument is not a valid agent identifier.
        """
        # Agent arguments must be...
        return  all([
                    # A string...
                    isinstance(argument, str),
                        
                    # Not be emtpy,..
                    len(argument) != 0,
                        
                    # And contain only alphanumeric cahracters, underscores, and dashes.
                    argument.replace("_", "").replace("-", "").isalnum()
                ])
        
    def _is_valid_generic_type_(self,
        argument:       Any,
        expected_type:  str
    ) -> bool:
        """# Is Generic Type Valid?
        
        Generic type validation for unknown or custom types.
        
        Falls back to basic validation when we don't have specific rules for a particular type.

        ## Args:
            * argument      (Any):  Argument being validated.
            * expected_type (str):  Expected type string.

        ## Returns:
            * bool:
                * True:     Argument passes basic validation.
                * False:    Argument is not valid.
        """
        return  any([
                    # Non-empty string.
                    (isinstance(argument, str) and len(argument) > 0),
                    
                    # Integer/Float.
                    isinstance(argument, (int, float)),
                    
                    # Boolean.
                    isinstance(argument, bool)
                ])
    
    def _is_valid_event_(self,
        argument:   Any
    ) -> bool:
        """# Is Event Valid?
        
        Check if argument is a valid event identifier.
        
        Events represent actions or state changes in the environment.
        Examples: "move", "pickup", "open_door", "press_button"

        ## Args:
            * argument  (Any):  Argument being validated.

        ## Returns:
            * bool:
                * True:     Argument is a valid event identifier.
                * False:    Argument is not a valid event identifier.
        """
        # Event arguments must be...
        return  all([
                    # A string...
                    isinstance(argument, str),
                        
                    # Not be emtpy,..
                    len(argument) != 0,
                        
                    # And contain only alphanumeric cahracters, underscores, and dashes.
                    argument.replace("_", "").replace("-", "").isalnum()
                ])
    
    def _is_valid_location_(self,
        argument:   Any
    ) -> bool:
        """# Is Location Valid?
        
        Check if argument is a valid location identifier.
        
        Locations can be:
            * String coordinates: "1,2", "(3,4)"
            * Named locations: "kitchen", "room_a"
            * Coordinate tuples: (1, 2)
        
        ## Args:
            * argument  (Any):  The argument to validate as a location
        
        ## Returns:
            * bool: 
                * True:     Argument is a valid location identifier.
                * False:    Argument is not valid as a location identifier.
        """
        # Location arguments must be either...
        return  any(
                    all([
                        # Strings that either...
                        isinstance(argument, str),
                        
                        any([
                            # Contain only alphanumeric cahracters, underscores, and dashes.
                            argument.replace("_", "").replace("-", "").isalnum(),
                            
                            # Or match coordinate representations such as "1,2" or "(1,2)"
                            bool(match(r"^\(?(-?\d+),\s*(-?\d+)\)?$", argument))
                        ])
                    ]),
                    all([
                        # Or Tuples/Lists...
                        isinstance(argument, (tuple, list)),
                        
                        # That have exactly two elements (two-dimensional locations)...
                        len(argument) == 2,
                        
                        # And all elements must be either integers or floats.
                        all(isinstance(element, (int, float)) for element in argument)
                    ])
                )
    
    def _is_valid_object_(self,
        argument:   Any
    ) -> bool:
        """# Is Object Valid?
        
        Check if argument is a valid object identifier.
        
        Objects are typically strings that represent entities in the environment.
        Valid patterns: "block1", "key_red", "door", etc.

        ## Args:
            * argument  (Any):  Argument being validated.

        ## Returns:
            * bool:
                * True:     Argument is a valid object.
                * False:    Argument is not a valid object.
        """
        # Object arguments must be...
        return  all([
                    # A string...
                    isinstance(argument, str),
                        
                    # Not be emtpy,..
                    len(argument) != 0,
                        
                    # And contain only alphanumeric cahracters, underscores, and dashes.
                    argument.replace("_", "").replace("-", "").isalnum()
                ])
        
    def _is_valid_value_type_(self,
        argument:   Any,
        base_type:  str
    ) -> bool:
        """# Is Type Valid?

        ## Args:
            * argument  (Any):  Argument being validated.
            * base_type (str):  Base type that argument must match (e.g., "color", "shape", "size").

        ## Returns:
            * bool:
                * True:     Argument is valid for thew specified value type.
                * False:    Argument is not valid.
        """
        # Simply return False if argument is not a string.
        if not isinstance(argument, str): return False
        
        # Define all valid values for common types used in symbolic reasoning.
        valid_values:   Dict[str, Set[str]] =   {
                                                    "color":        {"red", "blue", "yellow", "green", "orange", "purple", "black", "white", "gray", "brown", "pink", "cyan", "magenta"},
                                                    "direction":    {"north", "south", "east", "west", "up", "down", "left", "right", "forward", "backward", "ne", "nw", "se", "sw"},
                                                    "material":     {"wood", "metal", "plastic", "glass", "stone", "paper", "fabric", "rubber", "ceramic", "concrete"},
                                                    "shape":        {"square", "circle", "triangle", "rectangle", "diamond", "pentagon", "hexagon", "star", "oval", "ellipse", "cube", "sphere"},
                                                    "size":         {"small", "medium", "large", "tiny", "huge", "xs", "s", "m", "l", "xl", "micro", "mini", "big", "giant"},
                                                    "status":       {"open", "closed", "locked", "unlocked", "on", "off", "active", "inactive", "enabled", "disabled", "available", "busy"},
                                                    "type":         {"block", "key", "door", "wall", "agent", "goal", "obstacle", "button", "switcdh", "lever", "container", "box", "table", "chair"}
                                                }
        
        # If type is consistent with those defined...
        if base_type in valid_values:
            
            # Validate that it's classified as one defined.
            return argument.lower() in valid_values[base_type]
        
        # Otherise, at least require only alphanumeric cahracters, underscores, and dashes.
        return len(argument) > 0 and argument.replace("_", "").replace("-", "").isalnum()
    
    def _types_are_compatible_(self,
        variable_type:  str,
        expected_type:  str
    ) -> bool:
        """# Types Are Compatible?
        
        Check if a variable type is compatible with an expected type.
        
        This handles subtyping relationships where certain types can be used interchangeably in 
        predicate arguments.

        ## Args:
            * variable_type (str):  Variable's type constraint.
            * expected_type (str):  Expected type for this position.

        ## Returns:
            * bool:
                * True:     Types are compatible.
                * False:    Types are not compatible.
        """
        # If the types match, then they are of course compatible.
        if variable_type == expected_type: return True
        
        #Otherwise, define compatibility map...
        compatibility_rules:    Dict[str, Set[str]] =   {
                                                            "action":           {"event", "operation"},
                                                            "agent":            {"object", "actor", "player"},
                                                            "color_value":      {"value", "attribute_value"},
                                                            "event":            {"action", "transition"},
                                                            "item":             {"object", "artifact", "tool"},
                                                            "location":         {"object", "position", "coordinate"},
                                                            "material_value":   {"value", "attribute_value"},
                                                            "object":           {"agent", "location", "item", "entity"},
                                                            "shape_value":      {"value", "attribute_value"},
                                                            "size_value":       {"value", "attribute_value"},
                                                            "status_value":     {"value", "attribute_value"},
                                                            "type_value":       {"value", "attribute_value"},
                                                        }
        
        # Indicate if...
        return  any([
                    # Argument type is in rules and expected type is in compatible list.
                    variable_type in compatibility_rules and expected_type in compatibility_rules[variable_type],
                    
                    # Or expected type is in rules and argument type is in compatible list.
                    expected_type in compatibility_rules and variable_type in compatibility_rules[expected_type]
                ])
    
    def _validate_argument_(self,
        argument:       Any,
        expected_type:  str,
        position:       int
    ) -> bool:
        """# Validate Argument.

        ## Args:
            * argument      (Any):  Argument value being validated.
            * expected_type (str):  Expected type (e.g., "object", "color_value")
            * position      (int):  Position of argument (for error context).

        ## Returns:
            * bool:
                * True:     Argument is valid.
                * False:    Argument is not valid.
        """
        # If argument is of Variable type...
        if hasattr(argument, "__class__") and argument.__class__.__name__ == "Variable":
            
            # Extract variable type.
            variable_type:  Any =   getattr(argument, "variable_type", None)
            
            # Indicate...
            return  any([

                        # Argument has no variable type....
                        variable_type is None,
                        
                        # Or type is compatible.
                        self._types_are_compatible_(
                            variable_type = variable_type,
                            expected_type = expected_type
                        )
                    ])
        
        # Match expected type.
        match expected_type:
            
            # Agent.
            case "agent":       return self._is_valid_agent_(argument =     argument)
            
            # Event.
            case "event":       return self._is_valid_event_(argument =     argument)
            
            # Location.
            case "location":    return self._is_valid_location_(argument =  argument)
            
            # Object.
            case "object":      return self._is_valid_object_(argument =    argument)
            
            case _:
                
                # Values.
                if expected_type.endswith("_value"):    return self._is_valid_value_type_(
                                                            argument =  argument,
                                                            base_type = expected_type[:-6]
                                                        )
                
                # Generics.
                return self._is_valid_generic_type_(
                    argument =  argument,
                    expected_type = expected_type
                )
    
    @property
    def arity(self) -> int:
        """# Get Arity.
        
        Provide the arity of the predicate.

        ## Returns:
            * int:  Arity of predicate.
        """
        return len(self.arg_types)
    
    @property
    def type(self) -> PredicateType:
        """# Get Type.
        
        Provide the predicate's type.

        ## Returns:
            * PredicateType:    Predicate's type.
        """
        # Match arity.
        match self.arity:
            
            # Unary.
            case 1: return PredicateType.UNARY
            
            # Binary.
            case 2: return PredicateType.BINARY
            
            # Ternary.
            case 3: return PredicateType.TERNARY
            
            # N-ary.
            case _: return PredicateType.N_ARY
            
    def validate_arguments(self,
        arguments:  List[Any]
    ) -> bool:
        """# Validate Arguments.
        
        Vaidate that arguments match the expected types.

        ## Args:
            * arguments (List[Any]):    Arguments being validated.

        ## Returns:
            * bool:
                * True:     Arguments are valid for predicate.
                * False:    Arguments are not valid for predicate. 
        """
        # If arity is inconsistent, return False.
        if len(arguments) != self.arity: return False
        
        # Indicate that all arguments are valid/not.
        return  all([
                    self._validate_argument_(
                        argument = argument,
                        expected_type = expected_type,
                        position = p
                    )
                    for p, (argument, expected_type)
                    in enumerate(zip(arguments, self.arg_types))
                ])