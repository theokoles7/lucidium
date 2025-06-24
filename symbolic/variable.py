"""# lucidium.symbolic.logic.variable

This module defines a `Variable` class that represents symbolic variables within a neuro-symbolic 
reinforcement learning framework. These variables can participate in logical relations, be grounded 
to specific values, and optionally hold neural embeddings or types for reasoning and learning tasks.
"""

from typing import Any, Optional
from uuid   import uuid4, UUID

class Variable():
    """# Variable

    Represents a symbolic variable that may or may not be grounded to a specific value.

    Can optionally hold type information and be associated with neural embeddings.

    ## Attributes:
        * name      (str):              The name or identifier of the variable.
        * var_type  (Optional[str]):    The semantic type of the variable (e.g., "object", 
                                        "location").
        * value     (Optional[Any]):    The current grounded value of the variable.
        * id        (str):              Unique identifier for disambiguation purposes.
        * embedding (Optional[Any]):    Optional neural embedding for hybrid reasoning.
    """
    
    def __init__(self,
        name:       str,
        type:       Optional[str] = None,
        value:      Optional[Any] = None,
        embedding:  Optional[Any] = None
    ):
        """# Instantiate variable.

        ## Args:
            * name      (str):              Symbolic name of the variable.
            * type      (Optional[str]):    Semantic type/category of the variable.
            * value     (Optional[Any]):    Grounded value (if any).
            * embedding (Optional[Any]):    Neural embedding vector (if used).
        """
        # Assert that the name is a non-empty string.
        assert  isinstance(name, str)   and \
                name != ""              and \
                name.isidentifier(),            "Variable name must be a non-empty string and a valid identifier."
        
        # Define attributes.
        self._id_:          UUID =          uuid4()
        self._name_:        str =           name
        self._type_:        Optional[str] = type
        self._value_:       Optional[Any] = value
        self._embedding_:   Optional[Any] = embedding
        
    # PROPERTIES ===================================================================================
    
    @property
    def embedding(self) -> Optional[Any]:
        """# (Variable) Embedding

        The neural embedding associated with the variable, which can be used for hybrid reasoning 
        tasks that combine symbolic and neural representations.

        ## Returns:
            * Optional[Any]:    The neural embedding of the variable, or None if not specified.
        """
        return self._embedding_

    @property
    def id(self) -> UUID:
        """# (Variable) ID

        Unique identifier for the variable. This ensures that even if two variables have the same 
        name, they can still be distinguished within the framework.

        ## Returns:
            * UUID: The unique identifier of the variable.
        """
        return self._id_
    
    @property
    def is_grounded(self) -> bool:
        """# (Variable) Is Grounded?
        
        Indicate if variable is grounded.

        ## Returns:
            * bool: True if variable is grounded (is bounded to a value).
        """
        return self.value is not None
    
    @property
    def is_typed(self) -> bool:
        """# (Variable) Is Typed?

        Indicate if variable has a type.

        ## Returns:
            * bool: True if variable has a type.
        """
        return self.type is not None

    @property
    def name(self) -> str:
        """# (Variable) Name

        The symbolic name of the variable, used for logical reasoning and referencing within the 
        neurosymbolic framework.

        ## Returns:
            * str:  The name of the variable.
        """
        return self._name_

    @property
    def type(self) -> Optional[str]:
        """# (Variable) Type

        The semantic type of the variable, which can be used to categorize variables (e.g., 
        "object", "location") and guide reasoning processes.

        ## Returns:
            * Optional[str]:    The semantic type of the variable, or None if not specified.
        """
        return self._type_
    
    @property
    def value(self) -> Any:
        """# (Variable) Value

        ## Returns:
            * Any:  Variable's current value.
        """
        return self._value_
        
    # SETTERS ======================================================================================

    @embedding.setter
    def embedding(self, new_embedding: Optional[Any]) -> None:
        """# (Variable) Set Embedding

        Update the neural embedding of the variable.

        ## Args:
            * new_embedding (Optional[Any]): The new embedding for the variable.
        """
        self._embedding_ = new_embedding

    @name.setter
    def name(self, new_name: str) -> None:
        """# (Variable) Set Name

        Update the symbolic name of the variable.

        ## Args:
            * new_name (str): The new name for the variable.
        """
        self._name_ = new_name

    @type.setter
    def type(self, new_type: Optional[str]) -> None:
        """# (Variable) Set Type

        Update the semantic type of the variable.

        ## Args:
            * new_type (Optional[str]): The new type for the variable.
        """
        self._type_ = new_type
        
    @value.setter
    def value(self, new_value: Any) -> None:
        """# (Variable) Set Value

        Set or update the grounded value of the variable.

        ## Args:
            * new_value (Any): The new value to ground the variable to.
        """
        self._value_ = new_value
        
    # METHODS ======================================================================================
    
    def ground(self,
        value:  Any
    ) -> None:
        """# (Variable) Ground

        Ground the variable to a specific value.

        ## Args:
            * value (Any):  The value to ground the variable to.
        """
        self.value = value
        
    def is_compatible_with(self,
        other:  "Variable"
    ) -> bool:
        """# (Variable) Is Compatible With?

        ## Args:
            * other (Variable): Other variable to check compatibility with.

        ## Returns:
            * bool: True if the other variable has the same name and type, False otherwise.
        """
        # Check if the other object is an instance of Variable and compare names and types.
        if not isinstance(other, Variable): return False
        
        # Compare the names and types of the variables for compatibility.
        return self.name == other.name and self.type == other.type
        
    def to_dcit(self) -> dict:
        """# (Variable) To Dict

        Convert the variable to a dictionary representation.

        ## Returns:
            * dict: Dictionary containing the variable's attributes.
        """
        return {
            "id":           str(self.id),
            "name":         self.name,
            "type":         self.type,
            "value":        self.value,
            "embedding":    self.embedding.tolist()
                                if hasattr(self.embedding, "tolist")
                                else self.embedding
        }
        
    def unground(self) -> None:
        """# (Variable) Unground

        Remove the grounding of the variable, setting its value to None.
        """
        self.value = None
        
    # CLASS METHODS ================================================================================
    
    @classmethod
    def with_type(self,
        type:   str,
    ) -> "Variable":
        """# (Variable) With Type

        ## Args:
            * type  (str):  The semantic type of the variable.

        ## Returns:
            * Variable: A new Variable instance with the specified type.
        """
        # Create a new Variable instance with the specified type and no value or embedding.
        return  Variable(
                    name =  self.name,
                    type =  type
                )
        
    # DUNDERS ======================================================================================
    
    def __eq__(self, other: "Variable") -> bool:
        """# (Variable) Equality Check

        Check if this variable is equal to another variable based on its name and type.

        ## Args:
            * other (Variable): The object to compare against.

        ## Returns:
            * bool: True if the variables have the same name and type, False otherwise.
        """
        # Check if the other object is an instance of Variable and compare IDs.
        if not isinstance(other, Variable): return False
        
        # Compare the names and types of the variables for equality.
        return self.name == other.name and self.type == other.type
    
    def __hash__(self) -> int:
        """# (Variable) Hash

        Generate a hash value for the variable based on its name and type.

        ## Returns:
            * int:  The hash value of the variable.
        """
        return hash((self.name, self.var_type))
    
    def __repr__(self) -> str:
        """# (Variable) String Representation

        ## Returns:
            * str:  Readable string representation of the variable.
        """
        # Format the string representation of the variable.
        grounding:  str =   f"{self.name}:{self.value}" if self.is_grounded() else self.name
        
        # Format the type string if a type is specified.
        typing:     str =   f" [{self.var_type}]" if self.var_type else ""
        
        # Combine the grounded value and type into a string.
        return  f"""<Variable {grounding}{typing}>"""