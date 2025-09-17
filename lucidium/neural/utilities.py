"""# lucidium.neural.utilities

Utilities for creating/managing neural components.
"""

__all__ =   [
                "create_mlp",
                "extract_space_size"
            ]

from typing             import List, Tuple, Union

from gymnasium.spaces   import Discrete, Space
from torch              import dtype, float32
from torch.nn           import Linear, Module, ReLU, Tanh

def create_mlp(
    input_size:     int,
    output_size:    int,
    hidden_size:    Union[int, Tuple[int, ...]] =   (64, 64),
    activation:     type[Module] =                  ReLU,
    squash_output:  bool =                          False,
    bias:           bool =                          True,
    device:         str =                           "cpu",
    data_type:      dtype =                         float32
) -> List[Module]:
    """# Instantiate Multi-Layer Perceptron.

    ## Args:
        * input_size    (int):              Size of input.
        * output_size   (int):              Size of output.
        * hidden_size   (int | Tuple[int]): Size(s) of hidden connections. Defaults to (64, 64).
        * activation    (Module):           Activation function to use between layers. Defaults 
                                            to ReLU.
        * squash_output (bool):             If true, output will be squashed using hyberbolic 
                                            tangent. Defaults to False.
        * bias          (bool):             If true, layers will learn additive bias. Defaults 
                                                to True.
        * device        (str):              Torch device being used. Defaults to "cpu".
        * data_type     (torch.dtype):      Data type of tensor elements. Defaults to float32.
                                                
    ## Returns:
        * List[Module]: List of modules, initialized according to parameters.
    """
    # Validate parameters.
    assert input_size > 0,  f"MLP input size must be greater than zero."
    assert output_size > 0, f"MLP output size must be greater than zero."
    
    # Initialize modules list.
    modules:        List[Module] =  []
    
    # Ensure that hidden size specifications are a tuple.
    hidden_layers:  Tuple[int] =    (hidden_size,) if isinstance(hidden_size, int) else hidden_size
    
    # Concatenate connection sizes.
    layer_sizes:    Tuple[int] =    (input_size,) + hidden_layers + (output_size,)
    
    # For each input/output pair...
    for index in range(len(layer_sizes) - 1):
        
        # Create layer.
        modules.append(
            Linear(
                in_features =   layer_sizes[index],
                out_features =  layer_sizes[index + 1],
                bias =          bias,
                device =        device,
                dtype =         data_type
            )
        )
        
        # Add activation function for all but output layer.
        if index < len(layer_sizes) - 2: modules.append(activation())
        
    # If squashing, add tanh function.
    if squash_output: modules.append(Tanh())
    
    # Provide modules list.
    return modules

def extract_space_size(
    space:  Space
) -> int:
    """# Determine Space Size.

    ## Args:
        * space (Space):    Action/observation space.

    ## Returns:
        * int:  Size of first space dimension.
    """
    # If space is discrete, simply provide the `n` property.
    if isinstance(space, Discrete): return space.n
    
    # Otherwise, provide the first dimension's size.
    return space.shape[0]