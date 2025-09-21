"""# lucidium.registration.core.tests.entry_test

Registration entry test suite.
"""

from argparse                               import _SubParsersAction
from typing                                 import List

from pytest                                 import raises
from unittest.mock                          import Mock, patch

from lucidium.registration.core.entry       import Entry
from lucidium.registration.core.exceptions  import ParserNotConfiguredError

# Define test arguments.
test_tags:  List[str] = ["tag1", "tag2"]

# INITIALIZATION ===================================================================================

def test_entry_initialization_default() -> None:
    """# Test Default Initialization of Entry."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test")
    
    # Validate properties.
    assert entry.name == "test",    f"Entry name expected to be 'test', got {entry.name}"
    assert entry.tags == [],        f"Entry tags expected to be empty, got {entry.tags}"
    assert entry.parser is None,    f"Entry parser expected to be None, got {entry.parser}"
    
def test_entry_initialization_with_tags() -> None:
    """# Test Initialization of Entry with Tags."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test", tags = test_tags)
    
    # Validate properties.
    assert entry.name == "test",    f"Entry name expected to be 'test', got {entry.name}"
    assert entry.tags == test_tags, f"Entry tags expected to be {test_tags}, got {entry.tags}"
    assert entry.parser is None,    f"Entry parser expected to be None, got {entry.parser}"
    
def test_entry_initialization_with_parser(mock_subparser) -> None:
    """# Test Initialization of Entry with Tags."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test", tags = test_tags, parser = mock_subparser)
    
    # Validate properties.
    assert entry.name == "test",            \
        f"Entry name expected to be 'test', got {entry.name}"
    assert entry.tags == test_tags,         \
        f"Entry tags expected to be {test_tags}, got {entry.tags}"
    assert entry.parser is mock_subparser,  \
        f"Entry parser expected to be mock parser, got {entry.parser}"
        
# TAGS =============================================================================================

def test_entry_contains_tag() -> None:
    """# Test Tag Matching Functionality."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test", tags = test_tags)
    
    # Ensure that entry contains expected tags.
    assert entry.contains_tag("tag1"),      f"Entry expected to contain tag: 'tag1'"
    assert not entry.contains_tag("tag3"),  f"Entry expected to not contain tag: 'tag3'"
    
# PARSER HANDLER ===================================================================================

def test_entry_parser_handler() -> None:
    """# Test Parser Handler Registration."""
    # Define mock parser functionality.
    mock_subparser:     Mock =                  Mock(spec=_SubParsersAction)
    mock_subparser.dest =                       "test_dest"
    mock_add_parser:    Mock =                  Mock()
    mock_subparser.add_parser.return_value =    mock_add_parser
    
    def mock_parser(subparser): return subparser.add_parser("test_entry")
    
    # Initialize entry.
    entry:              Entry =                 Entry(name = "test_entry", parser = mock_parser)
    
    # Should not raise an exception.
    entry.register_parser(mock_subparser)
    
    # Verify the parser was called.
    mock_subparser.add_parser.assert_called_once_with("test_entry"),    \
        f"Argument handler not registered"
        
def test_entry_no_parser_handler(mock_subparser) -> None:
    """# Test Parser Handler Registration with No Parser Registered."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test_entry", parser = None)
    
    # Simulate registering parser.
    with raises(ParserNotConfiguredError) as exc_info: entry.register_parser(mock_subparser)
    
    # Ensure proper error message was raised.
    assert str(exc_info.value) == """Entry "test_entry" was not registered with an argument parser handler"""
    
# REPRESENTATION ===================================================================================

def test_entry_object_representation() -> None:
    """# Test Object Representation of Entry."""
    # Initialize entry.
    entry:  Entry = Entry(name = "test", tags = test_tags)
    
    # Define expected string.
    expected:   str =   "<TestEntry(tags = tag1,tag2)>"
    
    # Ensure representation is correct.
    assert str(entry) == expected,  \
        f"Entry object representation expected to be '{expected}', got '{str(entry)}'"