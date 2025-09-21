"""Tests for the base Registry class."""

from argparse                               import _SubParsersAction

from pytest                                 import raises
from unittest.mock                          import Mock, patch

from lucidium.registration.core.registry    import Registry
from lucidium.registration.core.entry       import Entry
from lucidium.registration.core.exceptions  import DuplicateEntryError

# MOCK CLASSES =====================================================================================

class ConcreteEntry(Entry):
    """Concrete Entry implementation for testing."""
    
    def __init__(self,
        name:   str,
        tags:   list =              None,
        parser: _SubParsersAction = None,
        **kwargs
    ):
        super().__init__(name = name, tags = tags or [], parser = parser)
        self.kwargs = kwargs


class ConcreteRegistry(Registry):
    """Concrete Registry implementation for testing."""
    
    def _create_entry_(self, **kwargs):
        return ConcreteEntry(**kwargs)

# INITIALIZATION ===================================================================================
    
def test_registry_initialization():
    """Test Registry initialization."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    assert registry.name == "test_registry",    \
        f"Registry name expected to be 'test_registry', got {registry.name}"
    assert registry.entries == {},              \
        f"Registry entries expected to be empty, got {registry.entries}"
    assert registry.is_loaded is False,         \
        f"Registry is_loaded expected to be False, got {registry.is_loaded}"
    assert len(registry) == 0,                  \
        f"Registry length expected to be 0, got {len(registry)}"

@patch('lucidium.registration.core.registry.get_child')
def test_registry_logger_initialization(mock_get_child):
    """Test that registry logger is properly initialized."""
    # Define mock logger.
    mock_logger:    Mock =  Mock()
    
    # Set mock get_child to return mock logger.
    mock_get_child.return_value = mock_logger
    
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Ensure logger was set correctly.
    mock_get_child.assert_called_once_with("test_registry-registry")


# PROPERTIES =======================================================================================
    
def test_entries_property_empty():
    """Test entries property when registry is empty."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Get entries.
    entries = registry.entries
    
    # Validate entries.
    assert entries == {},               \
        f"Registry entries expected to be empty dict, got {entries}"
    assert isinstance(entries, dict),   \
        f"Registry entries expected to be dict, got {type(entries)}"

def test_entries_property_returns_copy():
    """Test that entries property returns a copy."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register an entry.
    registry.register(name="test_entry", tags=["test"])
    
    # Get entries and modify the returned dict.
    entries = registry.entries
    entries["new_entry"] = Mock()
    
    # Original registry should be unchanged.
    assert "new_entry" not in registry.entries, \
        "Modifying entries property should not affect internal state."
    assert len(registry.entries) == 1,          \
        f"Registry entries expected to have 1 entry, got {len(registry.entries)}"

def test_is_loaded_property():
    """Test is_loaded property."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Initially should be False.
    assert registry.is_loaded is False, \
        f"Registry is_loaded expected to be False, got {registry.is_loaded}"
    
    # Simulate loading.
    registry._loaded_ = True
    
    # Now should be True.
    assert registry.is_loaded is True,  \
        f"Registry is_loaded expected to be True, got {registry.is_loaded}"

def test_name_property():
    """Test name property."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Validate name.
    assert registry.name == "test_registry", \
        f"Registry name expected to be 'test_registry', got {registry.name}"


# REGISTRATION =====================================================================================
    
def test_register_entry_success():
    """Test successful entry registration."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register entry.
    registry.register(name="test_entry", tags=["tag1", "tag2"])
    
    # Validate entry is registered.
    assert "test_entry" in registry,    \
        "Entry 'test_entry' should be registered in the registry."
    assert len(registry) == 1,          \
        f"Registry expected to have 1 entry, got {len(registry)}"
    
    # Extract and validate entry.
    entry = registry.get_entry("test_entry")
    assert entry.name == "test_entry",      \
        f"Entry name expected to be 'test_entry', got {entry.name}"
    assert entry.tags == ["tag1", "tag2"],  \
        f"Entry tags expected to be ['tag1', 'tag2'], got {entry.tags}"

def test_register_entry_with_parser():
    """Test entry registration with parser."""
    # Define mock parser function.
    def mock_parser(subparser): return subparser.add_parser("test")
    
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register entry with parser.
    registry.register(name="test_entry", parser=mock_parser)
    
    # Extract entry.
    entry:      Entry =     registry.get_entry("test_entry")
    
    # Validate entry.
    assert entry.parser == mock_parser, \
        "Entry parser should be the mock_parser function."

def test_register_duplicate_entry():
    """Test registering duplicate entry raises DuplicateEntryError."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register first entry.
    registry.register(name="duplicate_entry")
    
    # Attempt to register duplicate should raise error.
    with raises(DuplicateEntryError) as exc_info:
        registry.register(name="duplicate_entry")
    
    # Validate error message.
    error_message = str(exc_info.value)
    assert "duplicate_entry" in error_message,  \
        "Duplicate entry name should be in error message."
    assert "test_registry" in error_message,    \
        "Registry name should be in error message."

def test_register_multiple_entries():
    """Test registering multiple entries."""
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register multiple entries.
    registry.register(name="entry1", tags=["tag1"])
    registry.register(name="entry2", tags=["tag2"])
    registry.register(name="entry3", tags=["tag1", "tag2"])
    
    # Validate all entries are registered.
    assert len(registry) == 3,      \
        f"Registry expected to have 3 entries, got {len(registry)}"
    assert "entry1" in registry,    \
        "entry 1 expected to be registered"
    assert "entry2" in registry,    \
        "entry 2 expected to be registered"
    assert "entry3" in registry,    \
        "entry 3 expected to be registered"

@patch('lucidium.registration.core.registry.get_child')
def test_register_logging(mock_get_child):
    """Test that registration logs debug messages."""
    # Define mock logger.
    mock_logger = Mock()
    mock_get_child.return_value = mock_logger
    
    # Initialize registry.
    registry:   Registry =  ConcreteRegistry(name="test_registry")
    
    # Register an entry.
    registry.register(name="test_entry", tags=["test"])
    
    # Should have logged the registration.
    mock_logger.debug