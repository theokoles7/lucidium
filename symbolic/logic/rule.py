"""# lucidium.symbolic.logic.Rule

Define structure of logical rule representing antecedent -> consequent patterns.
"""

from re                         import match
from typing                     import Any, Dict, List, Optional, Set, Tuple

from symbolic.logic.expressions import CompoundExpression, Expression, PredicateExpression
from symbolic.logic.variable    import Variable
from symbolic.predicate         import Predicate, PredicateSet

class Rule():
    """# Rule.
    
    Represents a logical rule: antecedent -> consequent.
    
    Used for ingerence and predicate discovery.
    """
    
    def __init__(self,
        antecedent: Expression,
        consequent: Expression,
        confidence: float =         1.0,
        name:       Optional[str] = None
    ):
        """# Instantiate Logical Rule.

        ## Args:
            * antecedent    (Expression):               The precondition/trigger for which rule 
                                                        applies.
            * consequent    (Expression):               The outcome/result which rule's antecedent 
                                                        would cause/yield.
            * confidence    (float, optional):          Confidence in rule. Defaults to 1.0.
            * name          (Optional[str], optional):  Rule name. Defaults to None.
        """
        # Define attributes.
        self._antecedent_:  Expression =    antecedent
        self._consequent_:  Expression =    consequent
        self._confidence_:  float =         confidence
        self._name_:        str =           name if name else f"""rule_{id(self)}"""
        
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of rule.

        ## Returns:
            * str:  String representation of rule.
        """
        return f"""Rule({self.name}: {self})"""
        
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of rule.

        ## Returns:
            * str:  String representation of rule.
        """
        return f"""{self.antecedent} → {self.consequent}{f" [{self.confidence:.2f}]" if self.confidence < 1.0 else ""}"""
    
    def _apply_arc_consistency_(self,
        variable:       Variable,
        domains:        Dict[Variable, Set[Any]],
        predicate_set:  PredicateSet
    ) -> Set[Any]:
        """# Apply Arc Consistency.
        
        Apply arc consistency for a specific variable by removing values that cannot participate in 
        any valid assignment.

        ## Args:
            * variable      (Variable):     Variable to apply arc consistency to.
            * domains       (Dict[Variable, Set[Any]]): Current variable domains.
            * predicate_set (PredicateSet): Current predicate set.

        ## Returns:
            * Set[Any]: Reduced domain for the variable.
        """
        return  set(
                    value
                    for value
                    in domains[variable]
                    if  self._value_has_support_(
                            variable =      variable,
                            value =         value,
                            domains =       domains,
                            predicate_set = predicate_set
                        )
                )
    
    def _apply_constraint_propagation_(self,
        domains:        Dict[Variable, Set[Any]],
        predicate_set:  PredicateSet
    ) -> Dict[Variable, Set[Any]]:
        """# Apply Constraint Propagation.
        
        Use constraint propagation to reduce variable domains by enforcing consistency constraints 
        from the antecedent expression.

        ## Args:
            * domains       (Dict[Variable, Set[Any]]): Initial variable domains.
            * predicate_set (PredicateSet):             Current predicate set.

        ## Returns:
            * Dict[Variable, Set[Any]]: Reduced domains after constraint propagation.
        """
        # Copy domains for modification.
        propagated_domains: Dict[Variable, Set[Any]] =  {
                                                            variable: domain.copy()
                                                            for variable, domain in domains.items()
                                                        }
        
        # For simple constraint propagation, we'll use arc consistency.
        # Build initial arc queue (all pairs of variables that share constraints).
        variables_list = list(propagated_domains.keys())
        
        # Initialize changed flag for iterative refinement
        changed:            bool =                      True
        iterations:         int =                       0
        max_iterations:     int =                       10
        
        # While domain is still being changed...
        while changed and iterations < max_iterations:
            
            # Initial condition is that it is not changed, yet.
            changed =       False
            
            # Increment iteration count.
            iterations +=   1
            
            # For each variable, apply arc consistency.
            for variable in variables_list:
                original_size = len(propagated_domains[variable])
                propagated_domains[variable] = self._apply_arc_consistency_(
                    variable=variable,
                    domains=propagated_domains,
                    predicate_set=predicate_set
                )
                
                if len(propagated_domains[variable]) < original_size:
                    changed = True
                    
                # If domain becomes empty, no solution exists
                if not propagated_domains[variable]:
                    return {}
        
        return propagated_domains
    
    def _apply_structural_constraints_(self,
        variable:       Variable,
        domain:         Set[Any],
        predicate_set:  PredicateSet
    ) -> Set[Any]:
        """# Apply Structural Constraints.
        
        Apply constraints derived from the structure of the antecedent expression to further 
        restrict variable domains.

        ## Args:
            * variable      (Variable):     Variable being constrained.
            * domain        (Set[Any]):     Current domain for the variable.
            * predicate_set (PredicateSet): Current predicate set.

        ## Returns:
            Set[Any]: Constrained domain.
        """
        # Extract predicates that mention this variable.
        relevant_predicates:    List[PredicateExpression] = self._find_predicates_with_variable_(
                                                                variable = variable
                                                            )
        
        # Provide constrained domain set.
        return  set(
                    value
                    for value
                    in domain
                    if self._value_satisfies_structural_constraints_(
                        variable =              variable,
                        value =                 value,
                        relevant_predicates =   relevant_predicates,
                        predicate_set =         predicate_set
                    )
                )
        
    def _arguments_could_unify_(self,
        expression_argument:    Any,
        predicate_argument:     Any
    ) -> bool:
        """# Arguments Could Unify?
        
        Check if two arguments could potentially unify.

        Args:
            expression_argument (Any): Argument from expression, possibly variable.
            predicate_argument (Any): Argument from concrete predicate.

        Returns:
            bool:
                * True:     Arguments could unify.
                * False:    Arguments cannot unify.
        """
        # Indicate that...
        return  any([
                    # Expression argument is a variable (can unify with anything).
                    isinstance(expression_argument, Variable),
                    
                    # Or that arguments are equal.
                    expression_argument == predicate_argument
                ])
        
    def _assignment_viable_(self,
        partial_assignment:     Dict[Variable, Any],
        next_variable_index:    int,
        variables:              List[Variable],
        domains:                Dict[Variable, Set[Any]],
        predicate_set:          PredicateSet
    ) -> bool:
        """# Assignment is Viable?
        
        Check if a partial assignment is viable (i.e., could potentially be extended to a complete 
        valid assignment).

        ## Args:
            * partial_assignment    (Dict[Variable, Any]):      Current partial assignment.
            * next_variable_index   (int):                      Index of next variable to assign.
            * variables             (List[Variable]):           All variables being assigned.
            * domains               (Dict[Variable, Set[Any]]): Variable domains.
            * predicate_set         (PredicateSet):             Current predicate set.

        ## Returns:
            * bool:
                * True:     Assignment is viable.
                * False:    Assignment is not viable.
        """
        # Get keys of all assigned variables.
        assigned_variables:     Set[Variable] =     set(partial_assignment.keys())
        
        # Initialize list to track relevant predicates.
        relevant_predicates:    List[Expression] =  []
        
        # Define recursion.
        def find_fully_assigned_predicates(
            expression: Expression
        ) -> None:
            """# Find Fully Assigned Predicates.

            ## Args:
                * expression    (Expression):   Expression being searched.
            """
            # If expression is a predicate expression...
            if isinstance(expression, PredicateExpression):
                
                # Extract variables.
                predicate_variables:    Set[Variable] = expression.get_variables()
                
                # If assigned variables are non-empty subset of predicate variables...
                if predicate_variables and predicate_variables.issubset(assigned_variables):
                    
                    # Append to relevant predicates list.
                    relevant_predicates.append(expression)
                    
            # Otherwise, if compound expression...
            elif isinstance(expression, CompoundExpression):
                
                for operand in expression.operands: find_fully_assigned_predicates(expression = operand)
                
        # Commence recursion.
        find_fully_assigned_predicates(expression = self.antecedent)
        
        # Indicate if all fully assigned predicates are satisfied.
        return  all(
                    predicate_expression.evaluate(
                        predicate_set = predicate_set,
                        bindings =      partial_assignment
                    )
                    for predicate_expression
                    in relevant_predicates
                )
        
    def _backtrack_search_(self,
        variables:      List[Variable],
        domains:        Dict[Variable, Set[Any]],
        predicate_set:  PredicateSet
    ) -> List[Dict[Variable, Any]]:
        """# Backtrack Search.
        
        Use backtracking search with forward checking to find all valid variable assignments that 
        satisfy the antecedent.

        ##Args:
            * variables     (List[Variable]):           Variables to assign (in order).
            * domains       (Dict[Variable, Set[Any]]): Variable domains.
            * predicate_set (PredicateSet):             Current predicate set.

        ## Returns:
            * List[Dict[Variable, Any]]:    All valid, complete assignments.
        """
        # Initialize list of valid assignments.
        valid_assignments:  List[Dict[Variable, Any]] = []
        
        # Define recursion.
        def backtrack(
            assignment:     Dict[Variable, Any],
            variable_index: int
        ) -> None:
            """# Backtrack.

            ## Args:
                * assignment        (Dict[Variable, Any]):  Assignment to search.
                * variable_index    (int):                  Variable index to begin search at.
            """
            # Base Case: All variables assigned.
            if variable_index >= len(variables):
                
                # If assignment satisfies antecedent...
                if self.antecedent.evaluate(
                    predicate_set = predicate_set,
                    bindings =      assignment
                ):
                    # Append to valid assignments.
                    valid_assignments.append(assignment.copy())
                    
                # Return from recursion.
                return
                
            # Otherwise, get value at index.
            current_value:  Variable =  variables[variable_index]
            
            # Check if this variable exists in domains.
            if current_value not in domains:
                
                # Skip variables not in domains
                backtrack(assignment, variable_index + 1)
                return
            
            # For each value in the domain...
            for value in domains[current_value]:
                
                # Create a new assignment.
                new_assignment: Dict[Variable, Any] =   assignment.copy()
                
                # Assign respective value.
                new_assignment[current_value] =         value
                
                # If forward checking indicates that this assignment is viable...
                if self._assignment_viable_(
                    partial_assignment =    new_assignment,
                    next_variable_index =   variable_index + 1,
                    variables =             variables,
                    domains =               domains,
                    predicate_set =         predicate_set
                ):
                    
                    # Recursively assign remaining variables.
                    backtrack(assignment = new_assignment, variable_index = variable_index + 1)
        
        # Commence backtracking.
        backtrack(assignment = {}, variable_index = 0)
        
        # Provide any valid assignments found.
        return valid_assignments
    
    def _build_variable_domains_(self,
        variables:      Set[Variable],
        all_values:     Set[Any],
        predicate_set:  PredicateSet
    ) -> Dict[Variable, Set[Any]]:
        """# Build Variable Domains.
        
        Build initial domains for each variable based on type constraints and context from the 
        predicate set.

        ## Args:
            * variables     (Set[Variable]):    Variables for which domains will be built.
            * all_values    (Set[Any]):         All available values from predicate set.
            * predicate_set (PredicateSet):     Current predicate set for context.

        ## Returns:
            * Dict[Variable, Set[Any]]: Mapping from variables to their possible values.
        """
        # Initialize domain mappings.
        domains:        Dict[Variable, Set[Any]] =  {}
        
        # For each variable...
        for variable in variables:
            
            # Start will all possible values.
            domain:     Set[Any] =                  set(all_values)
            
            # If the variable has type constraints...
            if hasattr(variable, "variable_type") and variable.variable_type:
                
                # Apply type constraints.
                domain: Set[Any] =                  self._filter_by_type_(
                                                        domain =        domain,
                                                        variable_type = variable.variable_type
                                                    )
                
            # Apply structural constraints from antecedent.
            domains[variable] =                     self._apply_structural_constraints_(
                                                        variable =      variable,
                                                        domain =        domain,
                                                        predicate_set = predicate_set
                                                    )
        
        # Provide domain mappings.
        return domains
    
    def _could_unify_(self,
        predicate_expression:   PredicateExpression,
        predicate:              Predicate
    ) -> bool:
        """# Could Unify?
        
        Check if a predicate expression could potentially unify with a concrete predicate.

        ## Args:
            * predicate_expression  (PredicateExpression):  Predicate expression, possibly with 
                                                            variables.
            * predicate             (Predicate):            Concrete predicate.

        ## Returns:
            * bool: 
                * True:     Unification is possible.
                * False:    Unification is not possible.
        """
        # Extract predicate from expression.
        expression_predicate:   Predicate = predicate_expression._predicate_
        
        # Ensure that...
        return  all([
                    # Names match.
                    expression_predicate.name ==    predicate.name,
                    
                    # Arities match.
                    expression_predicate.arity ==   predicate.arity,
                    
                    # And that...
                    all([
                        
                        # Predicate arguments could unify...
                        self._arguments_could_unify_(
                            expression_argument =   expression_argument,
                            predicate_argument =    predicate_argument
                        )
                        
                        # For each predicate pair...
                        for expression_argument, predicate_argument
                        
                        # Between expression's predicate and given predicate.
                        in zip(expression_predicate.arguments, predicate.arguments)
                    ])
                ])
    
    def _enumerate_bindings_(self,
        variables:      Set[Variable],
        predicate_set:  PredicateSet
    ) -> List[Dict[Variable, Any]]:
        """# Enumerate Bindings.
        
        Enumerate possible variable bindings using sophisticated unification algorithm.
        
        This implementation uses constraint propagation and smart search rather than naive 
        enumeration. The algorithm:
            1. Extracts constraints from the antecedent expression
            2. Builds domains for each variable based on type constraints
            3. Uses constraint propagation to prune impossible combinations
            4. Employs backtracking search with forward checking
            5. Validates final bindings against the full antecedent

        ## Args:
            * variables     (Set[Variable]):    Variables used for bindings.
            * predicate_set (PredicateSet):     Set of predicates in which variables will be 
                                                grounded.

        ## Returns:
            * List[Dict[Variable, Any]]:    List of enumerated variable bindings.
        """
        # If no variables are provided, no bindings can be created.
        if not variables: return [{}]
        
        # Convert to list to ensure consistent ordering.
        variables_list:         List[Variable] =            list(variables)
        
        # 1: Extract all possible values from predicate set.
        all_values:             Set[Any] =                  self._extract_domain_values_(
                                                                predicate_set = predicate_set
                                                            )
        
        # 2: Build initial domains for each variable based on type constraints.
        variable_domains:       Dict[Variable, Set[Any]] =  self._build_variable_domains_(
                                                                variables =     set(variables_list),
                                                                all_values =    all_values,
                                                                predicate_set = predicate_set
                                                            )
        
        # 3: Apply constraint propagation to reduce domains.
        constrained_domains:    Dict[Variable, Set[Any]] =  self._apply_constraint_propagation_(
                                                                domains =       variable_domains,
                                                                predicate_set = predicate_set
                                                            )
                                    
        # 4: Use backtracking search to find valid bindings.
        valid_bindings:         List[Dict[Variable, Any]] = self._backtrack_search_(
                                                                variables =     variables_list,
                                                                domains =       constrained_domains,
                                                                predicate_set = predicate_set
                                                            )
        
        # Provide bindings.
        return valid_bindings
    
    def _extract_domain_values_(self,
        predicate_set:  PredicateSet
    ) -> Set[Any]:
        """# Extract Domain Values.
        
        Extract all possible values that could be used for variable bindings from the current 
        predicate set.

        ## Args:
            * predicate_set (PredicateSet): Set of predicates from which to extract values.

        ## Returns:
            * Set[Any]: Set of all values found in predicate arguments.
        """
        # Extract values from all predicates in the set.
        return set().union(*(predicate.arguments for predicate in predicate_set))
    
    def _extract_predicate_expressions_(self,
        expression: Expression
    ) -> List[PredicateExpression]:
        """# Extract Predicate Expressions.
        
        Extract all predicate expressions from a compound expression.

        ## Args:
            * expression    (Expression):   Expression from which predicates will be extracted.

        ## Returns:
            * List[PredicateExpression]:    List of predicates from expression.
        """
        # If predicate expression, simply return expression.
        if isinstance(expression, PredicateExpression):     return  [expression]
        
        # If compound expression...
        elif isinstance(expression, CompoundExpression):    
            
            # Then initialize list of expressions.
            expressions:    List[Expression] =  []
            
            # For each operand...
            for operand in expression.operands:
                
                # Add its components to the list.
                expressions.extend(self._extract_predicate_expressions_(expression = operand))
            
            # Provide the extracted list.
            return  expressions
        
        # Otherwise, return empty list.
        return []
    
    def _filter_by_type_(self,
        domain:         Set[Any],
        variable_type:  str
    ) -> Set[Any]:
        """# Filter By Type.
        
        Filter domain values based on variable type constraints.

        ## Args:
            * domain        (Set[Any]): Original domain of values.
            * variable_type (str):      Type constraint for the variable.

        ## Returns:
            * Set[Any]: Filtered domain containing only type-compatible values.
        """
        return  set(
                    value
                    for value
                    in domain
                    if  self._value_matches_type_(
                            value =         value,
                            variable_type = variable_type
                        )
                )
    
    def _find_bindings_(self,
        predicate_set:  PredicateSet
    ) -> List[Dict[Variable, Any]]:
        """# Find Bindings.
        
        Provide all variable bindings that satisfy antecedent.

        ## Args:
            * predicate_set (PredicateSet): Set of predicates being evaluated under antecedent.

        ## Returns:
            * List[Dict[Variable, Any]]:    Variable bindings that satisfy antecedent.
        """
        # If there are no variables...
        if not self.antecedent.get_variables():
            
            # If antecendent is true for predicate set.
            if  self.antecedent.evaluate(predicate_set = predicate_set):
                
                # Return empty variable set.
                return [{}]
            
            # Otherwise, return empty list.
            return []
        
        # Otherise, return enumerated bindings of variables.
        return  self._enumerate_bindings_(
                    variables =     self.antecedent.get_variables(),
                    predicate_set = predicate_set
                )
        
    def _find_predicates_with_variable_(self,
        variable:   Variable
    ) -> List[PredicateExpression]:
        """# Find Predicates with Variable.
        
        Find all predicate expressions in the antecedent that contain the given variable.

        ## Args:
            * variable  (Variable): Variable to search for.

        ## Returns:
            * List[PredicateExpression]:    Predicate expressions containing the variable.
        """
        # Initialize list of predicates.
        predicates: List[PredicateExpression] = []
        
        # Define recursive extraction.
        def extract_predicates(
            expression: Expression
        ) -> None:
            """# Extract Predicates.
            
            Extract predicates from expressions. Recurse on compound expressions.

            ## Args:
                * expression    (Expression):   Expression from which predicates will be extracted.
            """
            # If normal predicate expression...
            if isinstance(expression, PredicateExpression):
                
                # If the expression contains variables...
                if variable in expression.get_variables():
                    
                    # Append expression.
                    predicates.append(expression)
                    
            # If compound expression...
            elif isinstance(expression, CompoundExpression):
                
                # Recurse on each operand.
                for operand in expression.operands: extract_predicates(expression = operand)
        
        # Extract predicates.
        extract_predicates(self.antecedent)
        
        # Provide predicates with variable.
        return predicates
    
    def _partial_binding_viable_(self,
        predicate_expression:   PredicateExpression,
        partial_binding:        Dict[Variable, Any],
        predicate_set:          PredicateSet
    ) -> bool:
        """# Partial Binding Viable?
        
        Check if a partial variable binding could potentially lead to a successful unification with 
        predicates in the set.

        ## Args:
            * predicate_expression  (PredicateExpression):  Predicate expression to check.
            * partial_binding       (Dict[Variable, Any]):  Partial variable binding to test.
            * predicate_set         (PredicateSet):         Current predicate set.

        ## Returns:
            * bool:
                * True:     Partial binding could work.
                * False:    Partial binding will not work.
        """
        # Apply partial binding to the predicate expression.
        partially_bound:    PredicateExpression =   predicate_expression.substitute(
                                                        bindings = partial_binding
                                                    )
        
        # Indicate if any of the predicates in the set could match.
        return  any(
                    self._could_unify_(
                        predicate_expression =  predicate_expression,
                        predicate =             predicate
                    )
                    for predicate
                    in predicate_set
                )
        
    def _predicate_has_support_(self,
        predicate_expression:   PredicateExpression,
        partial_assignment:     Dict[Variable, Any],
        domains:                Dict[Variable, Set[Any]],
        predicate_set:          PredicateSet
    ) -> bool:
        """# Predicate Has Support?
        
        Check if a predicate expression can be satisfied given a partial assignment and remaining 
        variable domains.

        ## Args:
            * predicate_expression  (PredicateExpression):      Predicate being checked.
            * partial_assignment    (Dict[Variable, Any]):      Partial variable assignment.
            * domains               (Dict[Variable, Set[Any]]): Remaining variable domains.
            * predicate_set         (PredicateSet):             Current predicate set.

        ## Returns:
            * bool:
                * True:     Predicate can be satisfied.
                * False:    Predicate will not be satisfied.
        """
        # Apply partial assignment.
        partially_bound:        PredicateExpression =   predicate_expression.substitute(
                                                            bindings =  partial_assignment
                                                        )
        
        # Get remaining variables.
        remaining_variables:    Set[Variable] =         partially_bound.get_variables()
        
        # If there are no remaining variables...
        if not remaining_variables:
            
            # Indicate if predicate set has been satisfied.
            return  partially_bound.evaluate(
                        predicate_set = predicate_set
                    )
            
        # Otherwise, check if there's a way to bind remaining variables.
        # TODO: This requires a more sophisticated analysis.
        return True
    
    def _revise_domain_(self,
        variable_i:     Variable,
        variable_j:     Variable,
        domains:        Dict[Variable, Set[Any]],
        predicate_set:  PredicateSet
    ) -> bool:
        """# Revise Domain.
        
        Revise domain of var_i by removing values that have no support in var_j's domain.

        ## Args:
            * variable_i    (Variable):     Variable whose domain is being revised.
            * variable_j    (Variable):     Variable who will be removed from domain.
            * domains       (Dict[Variable, Set[Any]]): Domain of first variable.
            * predicate_set (PredicateSet): Current predicate set.

        ## Returns:
            * bool:
                * True:     Domain has been revised.
                * False:    Domain was not revised.
        """
        # Set flag to indicate if domain is revised, and initialize list of values to remove.
        revised:            bool =      False
        values_to_remove:   Set[Any] =  set()
        
        # For each value of i...
        for value_i in domains[variable_i]:
            
            # Set flag to indicate support being found.
            has_support:    bool =  False
            
            # For each value of j..
            for value_j in domains[variable_j]:
                
                # Check if this combination is consistent with constraints
                if self._variables_are_consistent_(
                    variable_i =    variable_i,
                    value_i =       value_i,
                    variable_j =    variable_j,
                    value_j =       value_j,
                    predicate_set = predicate_set
                ):
                    
                    # Value has support.
                    has_support = True
                    break
            
            # If support was not confirmed...
            if not has_support:
                
                # Add to list of values being removed.
                values_to_remove.add(value_i)
                
                # Indicate that domain has been revised.
                revised = True
        
        # Remove variable not supported.
        domains[variable_i] -= values_to_remove
        
        # Provide (revised) domain.
        return revised
        
    def _value_has_support_(self,
        variable:       Variable,
        value:          Any,
        domains:        Dict[Variable, Set[Any]],
        predicate_set:  PredicateSet
    ) -> bool:
        """# Value has Support?
        
        Check if a value for a variable has support (i.e., there exist values for other variables 
        that make the assignment consistent).

        ## Args:
            * variable      (Variable):                 Variable being checked.
            * value         (Any):                      Value being checked for support.
            * domains       (Dict[Variable, Set[Any]]): Current variable domains.
            * predicate_set (PredicateSet):             Current predicate set.

        ## Returns:
            * bool:
                * True:     Value has support.
                * False:    Value has no support.
        """
        # Create partial assignment.
        partial_assignment:     Dict[Variable, Any] =       {variable: value}
        
        # Find predicates that involve this variable.
        relevant_predicates:    List[PredicateExpression] = self._find_predicates_with_variable_(
                                                                variable =  variable
                                                            )
        
        # Indicate that...
        return  all(
                    # There is support...
                    self._predicate_has_support_(
                        predicate_expression =  predicate_expression,
                        partial_assignment =    partial_assignment,
                        domains =               domains,
                        predicate_set =         predicate_set
                    )
                    
                    # For each predicate...
                    for predicate_expression
                    
                    # In relevant predicates provided.
                    in relevant_predicates
                )
        
    def _value_matches_type_(self,
        value:          Any,
        variable_type:  str
    ) -> bool:
        """# Value Matches Type?
        
        Check if a value is compatible with a variable type constraint.

        ## Args:
            * value         (Any):  Value to verify.
            * variable_type (str):  Type constraint.

        ## Returns:
            * bool:
                * True:     Value is compatible with type.
                * False:    Value is not compatible with type.
        """
        # Match type.
        match variable_type:
            
            # Object arguments must be...
            case "object":      return  all([
                                            # A string...
                                            isinstance(value, str),
                                                
                                            # And contain only alphanumeric cahracters, underscores, and dashes.
                                            value.replace("_", "").replace("-", "").isalnum()
                                        ])
            
            # Location arguments must be either...
            case "location":    return  any(
                                            all([
                                                # Strings that either...
                                                isinstance(value, str),
                                                
                                                any([
                                                    # Contain only alphanumeric cahracters, underscores, and dashes.
                                                    value.replace("_", "").replace("-", "").isalnum(),
                                                    
                                                    # Or match coordinate representations such as "1,2" or "(1,2)"
                                                    bool(match(r"^\(?(-?\d+),\s*(-?\d+)\)?$", value))
                                                ])
                                            ]),
                                            all([
                                                # Or Tuples/Lists...
                                                isinstance(value, (tuple, list)),
                                                
                                                # That have exactly two elements (two-dimensional locations)...
                                                len(value) == 2,
                                                
                                                # And all elements must be either integers or floats.
                                                all(isinstance(element, (int, float)) for element in value)
                                            ])
                                        )
            
            # Generic values will...
            case _:             # Values.
                                if variable_type.endswith("_value"):
                                    
                                    # Simply return False if argument is not a string.
                                    if not isinstance(value, str): return False
                                    
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
                                    if variable_type in valid_values:
                                        
                                        # Validate that it's classified as one defined.
                                        return value.lower() in valid_values[variable_type]
                                    
                                    # Otherise, at least require only alphanumeric cahracters, underscores, and dashes.
                                    return len(value) > 0 and value.replace("_", "").replace("-", "").isalnum()
                                
                                # Generics.
                                return  any([
                                    # Non-empty string.
                                    (isinstance(value, str) and len(value) > 0),
                                    
                                    # Integer/Float.
                                    isinstance(value, (int, float)),
                                    
                                    # Boolean.
                                    isinstance(value, bool)
                                ])
                                
    def _value_satisfies_structural_constraints_(self,
        variable:               Variable,
        value:                  Any,
        relevant_predicates:    List[PredicateExpression],
        predicate_set:          PredicateSet
    ) -> bool:
        """# Value Satisfies Structural Constraints?
        
        Check if a value for a variable satisfies structural constraints from the predicates that 
        mention that variable.

        ## Args:
            * variable              (Variable):                     Variable being bound.
            * value                 (Any):                          Proposed value for the variable.
            * relevant_predicates   (List[PredicateExpression]):    Predicates mentioning variable.
            * predicate_set         (PredicateSet):                 Current predicate set.

        ## Returns:
            * bool:
                * True:     Value satisfies constraints.
                * False:    Value does not satisfy constraints.
        """
        # For each predicate that mentions this variable...
        for expression in relevant_predicates:
            
            # Create a partial binding.
            partial_binding:    Dict[Variable, Any] =   {variable: value}
            
            # If even one binding will not lead to a match...
            if not self._partial_binding_viable_(
                predicate_expression =  expression,
                partial_binding =       partial_binding,
                predicate_set =         predicate_set
            ):
                
                # Unsatisfactory.
                return False
            
        # Otherwise, all bindings can potentially lead to matches.
        return True
    
    def _variables_are_consistent_(self,
        variable_i:     Variable,
        variable_j:     Variable,
        value_i:        Any,
        value_j:        Any,
        predicate_set:  PredicateSet
    ) -> bool:
        """# Are Variables Consistent?
        
        Check if two variable-value assignments are consistent with constraints.

        ## Args:
            * variable_i    (Variable):     First variable being checked.
            * variable_j    (Variable):     Second variable being checked.
            * value_i       (Any):          Value of variable 1.
            * value_j       (Any):          Value of variable 2.
            * predicate_set (PredicateSet): Current predicate set.

        ## Returns:
            bool:
                * True:     Variable are consistent.
                * False:    Variables are not consistent.
        """
        # Initialize partial assignment.
        partial_assignment: Dict[Variable, Any] =   {
                                                        variable_i: value_i,
                                                        variable_j: value_j
                                                    }
    
        # Find predicates that involve both variables
        shared_predicates = []
        predicate_expressions = self._extract_predicate_expressions_(self.antecedent)
        
        for pred_expr in predicate_expressions:
            variables_in_predicate = pred_expr.get_variables()
            if variable_i in variables_in_predicate and variable_j in variables_in_predicate:
                shared_predicates.append(pred_expr)
        
        # Check if partial assignment satisfies shared constraints
        for pred_expr in shared_predicates:
            try:
                # Apply partial substitution
                partially_bound = pred_expr.substitute(partial_assignment)
                
                # If fully grounded, check if it exists in predicate set
                if not partially_bound.get_variables():
                    if not partially_bound.evaluate(predicate_set):
                        return False
                # If still has variables, check if it could potentially be satisfied
                else:
                    if not self._could_be_satisfied_(partially_bound, predicate_set):
                        return False
            except:
                return False
        
        return True
    
    def _variables_share_constraint_(self,
        variable_1: Variable,
        variable_2: Variable
    ) -> bool:
        """# Do Variables Share Constraint?

        ## Args:
            * variable_1    (Variable): First variable.
            * variable_2    (Variable): Second variable.

        ## Returns:
            * bool:
                * True:     Variables share constraint.
                * False:    Variables do not share constraint.
        """
        # Extract all predicate expressions from antecedent
        predicate_expressions = self._extract_predicate_expressions_(self.antecedent)
        
        # For each expression extractedl...
        for expression in predicate_expressions:
            
            # Extract its variables.
            variables_in_predicate = expression.get_variables()
            
            # If both variables are included in predicate...
            if  variable_1 in variables_in_predicate and \
                variable_2 in variables_in_predicate: 
                    
                # Variable share constraint.
                return True
            
        # Variable do not share constraint.
        return False
        
    @property
    def antecedent(self) -> Expression:
        """# Get Antecedent.
        
        Provide antecendent expression of rule.

        ## Returns:
            * Expression:   Rule's antecedent.
        """
        return self._antecedent_
    
    def apply(self,
        predicate_set:  PredicateSet
    ) -> List[Predicate]:
        """# Apply Rule.
        
        Apply rule to predicate set.

        ## Args:
            * predicate_set (PredicateSet): Predicate set being applied to rule.

        ## Returns:
            * List[Predicate]:  List of predicates formed from rule and predicate set.
        """
        # Initialize list of derived predicates.
        predicates: List[Predicate] =   []
        
        # For each binding in list...
        for bindings in self._find_bindings_(predicate_set = predicate_set):
            
            # Apply bindings to concequent.
            grounded_consequent:    Expression =    self.consequent.substitute(
                                                        bindings =  bindings
                                                    )
            
            # If grounded consequent is a predicate expression...
            if isinstance(grounded_consequent, PredicateExpression):
                
                # Extract the predicate.
                predicate:  Predicate = grounded_consequent._predicate_
                
                # Adjust confidence.
                predicate:  Predicate = Predicate(
                                            name =          predicate.name,
                                            arguments =     predicate.arguments,
                                            signature =     predicate.signature,
                                            confidence =    predicate.confidence * self.confidence
                                        )
                
                # If predicate has not already been discovered, append it to derivation list.
                if not predicate_set.contains(predicate = predicate): predicates.append(predicate)
                
        # Provide derived predicates.
        return predicates
    
    @property
    def confidence(self) -> float:
        """# Get Confidence.
        
        Provide confidence of rule.

        ## Returns:
            * float:    Rule's confidence.
        """
        return self._confidence_
    
    @property
    def consequent(self) -> Expression:
        """# Get Consequent.
        
        Provide consequent expression of rule.

        ## Returns:
            * Expression:   Rule's consequent.
        """
        return self._consequent_
    
    def get_variables(self) -> Set[Variable]:
        """# Get Variables.
        
        Get all variables in this rule for which antecedent or consequent is true.

        ## Returns:
            * Set[Variable]:    Set of rule variables.
        """
        return self.antecedent.get_variables() | self.consequent.get_variables()
    
    @property
    def name(self) -> str:
        """# Get Name.
        
        Provide rule name.

        ## Returns:
            * str:  Name of rule.
        """
        return self._name_