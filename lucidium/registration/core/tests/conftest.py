"""# lucidium.registration.core.tests.conftest

Registration core tests configuration.
"""

from argparse       import _SubParsersAction
from typing         import Dict

from pytest         import fixture
from unittest.mock  import Mock

# Define mock parser class.
class MockSubParser:
    """# Mock Sub-Parser
    
    Mock subparser for testing argument parser registration.
    """
    
    def __init__(self):
        """# Instantiate Mock Parser."""
        # Initialize parser map.
        self.parsers:   Dict[str, Mock] =   {}
        
        # Define destination.
        self.dest:      str =               "mock_dest"
    
    def add_parser(self,
        name:   str,
        **kwargs
    ) -> Mock:
        """# Simulate Adding a Parser."""
        # Define mock parser.
        mock_parser = Mock(spec = _SubParsersAction)
        
        # Simpulate adding an argument.
        mock_parser.add_argument = Mock()
        
        # Define parser properties.
        mock_parser.name =      name
        mock_parser.kwargs =    kwargs
        
        # Add parser to map.
        self.parsers[name] =    mock_parser
        
        # Provide mock parser.
        return mock_parser


@fixture
def mock_subparser():
    """Mock Sub-Parser Instance."""
    return MockSubParser()