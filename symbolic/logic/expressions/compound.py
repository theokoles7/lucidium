"""# lucidium.symbolic.logic.expressions.CompoundExpression

Define structure of compound expressions.
"""

from typing                                 import Any, List, Dict, Set

from symbolic.logic.expressions.__base__    import Expression
from symbolic.logic.expressions.predicate   import PredicateExpression
from symbolic.logic.operator                import Operator
from symbolic.logic.variable                import Variable
from symbolic.predicate                     import PredicateSet

class CompoundExpression(Expression):
    """# Compound Expression.
    
    Compound lgocial expression with operator and operands.
    """
    
    def __init__(self,
        operator:   Operator,
        operands:   List[Expression]
    ):
        """# Instantiate Compound Expression.

        ## Args:
            * operator  (LogicalOperator):  Expression operator.
            * operands  (List[Expression]): Expression operands, evaluated by operator.
        """
        # Define operands and operator.
        self._operator_:    Operator =          operator
        self._operands_:    List[Expression] =  operands
        
        # Validate parameters.
        self._validate_arity_()
        
    def __repr__(self) -> str:
        """# Get String.
        
        Provide string representation of compound expression.

        ## Returns:
            * str:  String representation of compound expression.
        """
        # Return simple string if NOT operator.
        if self.operator == Operator.NOT:   return f"""{self.operator.value}{self.operands[0]}"""
        
        # Otherwse, return operands joined by operator.
        return f"""{self.operator.value.join(str(operand) for operand in self.operands)}"""
        
    def __str__(self) -> str:
        """# Get String.
        
        Provide string representation of compound expression.

        ## Returns:
            * str:  String representation of compound expression.
        """
        return f"""CompoundExpression({self.operator}, {self.operands})"""
        
    def _demorgen_(self,
        operand:    Expression
    ) -> Expression:
        """# Demorgen.
        
        Apply De Morgan's law for NOT operator.

        ## Args:
            * operand   (Expression):   Operands being applied.

        ## Returns:
            * Expression:   CNF expression.
        """
        # If operand is a compound expression...
        if isinstance(operand, CompoundExpression):
            
            # Match operator.
            match operand.operator:
                
                # AND.
                case Operator.AND:
                    
                    # Return De Morgan's theorem.
                    return  CompoundExpression(
                                operator =  Operator.OR,
                                operands =  [
                                                CompoundExpression(
                                                    operator =  Operator.NOT,
                                                    operands =  [operand]
                                                )
                                                for operand
                                                in operand.operands
                                            ]
                            )
                
                # NOT.
                case Operator.NOT:
                    
                    # Return operand.
                    return  operand.operands[0]
                
                # OR.
                case Operator.OR:
                    
                    # Return De Morgan's theorem.
                    return  CompoundExpression(
                                operator =  Operator.AND,
                                operands =  [
                                                CompoundExpression(
                                                    operator =  Operator.NOT,
                                                    operands =  [operand]
                                                )
                                                for operand
                                                in operand.operands
                                            ]
                            )
        
        # Otherwise, return compound expression anyway.
        return  CompoundExpression(
                    operator =  Operator.NOT,
                    operands =  [operand]
                )
        
    def _distribute_or_over_and_(self,
        operands:   List[Expression]
    ) -> Expression:
        """# Distribute OR Over AND.
        
        Distribute OR over AND to maintain CNF.

        ## Args:
            * operands  (List[Expression]): Operands being distributed.

        ## Returns:
            * Expression:   Expression distributed over AND operators.
        """
        # TODO: implement full version
        return  CompoundExpression(
                    operator =  Operator.OR,
                    operands =  operands
                )
                
    def _validate_arity_(self) -> None:
        """# Validate Arity.
        
        Ensure that the arity of operands is consistent with the type of operator provided.
        """
        # Match operator type.
        match self.operator:
            
            # Unary.
            case Operator.NOT:
                
                # Assert that there is exactly one operand.
                assert len(self._operands_) == 1,   f"NOT operator requires exactly one operand, got {len(self._operands_)}"
            
            # Binary.
            case Operator.IMPLIES | Operator.IFF:
                
                # Assert that there are exactly two operands.
                assert len(self._operands_) == 2,   f"IMPLIES and IFF operators require exactly two operands, got {len(self._operands_)}"
                
            # Ternary +.
            case Operator.AND | Operator.OR:
                
                # Assert that there are at least two operands.
                assert len(self._operands_) >= 2,   f"AND and OR operators require at least two operands, got {len(self._operands_)}"
    
    def evaluate(self,
        predicate_set:  PredicateSet,
        bindings:       Dict[Variable, Any] =   None
    ) -> bool:
        """# Evaluate Expression.

        ## Args:
            * predicate_set (PredicateSet):                         Set of predications on which 
                                                                    expression will be evaluated.
            * bindings      (Dict[LogicVariable, Any], optional):   Variable bindings which will be 
                                                                    evaluated in expression. 
                                                                    Defaults to None.

        ## Returns:
            * bool:
                * True:     Variable bindings satisfy predicate constraints.
                * False:    Variable bindings do not satisfy predicate constraints.
        """
        # Match operator.
        match self.operator:
            
            # AND.
            case Operator.AND:
                
                # Evaluate that all operands are true.
                return      all(
                                operand.evaluate(
                                    predicate_set = predicate_set,
                                    bindings =      bindings
                                ) 
                                for operand 
                                in self._operands_
                            )
            
            # IFF.
            case Operator.IFF:
                
                # Evaluate that both operands evaluate to the same value.
                return      self._operands_[0].evaluate(
                                predicate_set = predicate_set,
                                bindings =      bindings
                            )   \
                            ==  \
                            self._operands_[1].evaluate(
                                predicate_set = predicate_set,
                                bindings =      bindings
                            )
            
            # IMPLIES.
            case Operator.IMPLIES:
                
                # Evaluate that antecedent if not true or consequent is true.
                return  not self._operands_[0].evaluate(        # Antecedent
                                predicate_set = predicate_set,
                                bindings =      bindings
                            )   \
                            or  \
                            self._operands_[1].evaluate(        # Consequent
                                predicate_set = predicate_set,
                                bindings =      bindings
                            )
            
            # NOT.
            case Operator.NOT:
                
                # Evaluate that operand is not true.
                return  not self._operands_[0].evaluate(
                                predicate_set = predicate_set,
                                bindings =      bindings
                            )
            
            # OR.
            case Operator.OR:
                
                # Evaluate that at least one operand is true.
                return      any(
                                operand.evaluate(
                                    predicate_set = predicate_set,
                                    bindings =      bindings
                                ) 
                                for operand 
                                in self._operands_
                            )
            
            # Raise error for invalid operator.
            case _: ValueError(f"Invalid expression operator: {self.operator}")
            
    def get_variables(self) -> Set[Variable]:
        """# Get Variables.
        
        Provide all variables from operands.

        ## Returns:
            * Set[Variable]:    Set of operand variables.
        """
        # Initialize empty set for storing variables.
        variables:  Set =   set()
        
        # Add variables from each operand.
        variables.update(operand.get_variables() for operand in self._operands_)
        
        # Provide variables set.
        return variables
    
    @property
    def operands(self) -> List[Expression]:
        """# Get Operands.
        
        Provide expression operands.

        ## Returns:
            * List[Expression]: List of expression oprands.
        """
        return self._operands_
    
    @property
    def operator(self) -> Operator:
        """# Get Operator.

        ## Returns:
            * Operator: Expression's operator.
        """
        return self._operator_
    
    def substitute(self,
        bindings:   Dict[Variable, Any]
    ) -> "CompoundExpression":
        """# Substitue Bindings.
        
        Substitue expression bindings.

        ## Args:
            * bindings  (Dict[Variable, Any]):  New expression variable bindings.

        ## Returns:
            * PredicateExpression:  New expression with substituted variable bindings.
        """
        return  CompoundExpression(
                    operator =  self.operator,
                    operands =  [
                                    operand.to_cnf()
                                    for operand
                                    in self._operands_
                                ]
                )
        
    def to_cnf(self) -> Expression:
        """# Conjunctive Normal Form.
        
        Convert to conjunctive normal form using standard transformation.

        ## Returns:
            * Expression:   Expression in CNF.
        """
        # Convert operands to CNF.
        cnf_operands:   List[Expression] =  [operand.to_cnf() for operand in self._operands_]
        
        # Match operator.
        match self.operator:
            
            # AND.
            case Operator.AND:
                
                # Evaluate that all operands are true.
                return      CompoundExpression(
                                operator =  Operator.AND,
                                operands =  cnf_operands
                            )
            
            # IFF.
            case Operator.IFF:
                
                # Evaluate that both operands evaluate to the same value.
                return      CompoundExpression(
                                operator =  Operator.AND,
                                operands =  [
                                                CompoundExpression(
                                                    operator =  Operator.IMPLIES,
                                                    operands =  [
                                                                    cnf_operands[0],
                                                                    cnf_operands[1]
                                                                ]
                                                ),
                                                CompoundExpression(
                                                    operator =  Operator.IMPLIES,
                                                    operands =  [
                                                                    cnf_operands[1],
                                                                    cnf_operands[0]
                                                                ]
                                                )
                                            ]
                            ).to_cnf()
            
            # IMPLIES.
            case Operator.IMPLIES:
                
                # Evaluate that antecedent if not true or consequent is true.
                return      CompoundExpression(
                                operator =  Operator.OR,
                                operands =  [
                                                CompoundExpression(
                                                    operator =  Operator.NOT,
                                                    operands =  [
                                                                    cnf_operands[0]
                                                                ]
                                                ),
                                                cnf_operands[1]
                                            ]
                            ).to_cnf()
            
            # NOT.
            case Operator.NOT:
                
                # Evaluate that operand is not true.
                return      self._demorgen_(
                                operand =   cnf_operands[0]
                            )
            
            # OR.
            case Operator.OR:
                
                # Evaluate that at least one operand is true.
                return      self._distribute_or_over_and_(
                                operands =  cnf_operands
                            )
            
            # Raise error for invalid operator.
            case _: ValueError(f"Invalid expression operator: {self.operator}")