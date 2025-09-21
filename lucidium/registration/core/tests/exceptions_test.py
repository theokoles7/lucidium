"""# lucidium.registration.core.tests.exceptions_test

Registration exceptions test suite.
"""

from typing                                 import List, Tuple

from pytest                                 import raises

from lucidium.registration.core.exceptions  import *

# REGISTRATION ERROR ===============================================================================

def test_registration_error_inheritance() -> None:
    """# Test that Registration Error Inherits from Exception."""
    # instantiate error.
    error:  RegistrationError = RegistrationError("test message")
    
    # Ensure inheritance.
    assert isinstance(error, Exception),    \
        f"RegistrationError no longer inherits from Exception"
    assert str(error) == "test message",    \
        f"RegistrationError message expected to be 'test message', got {str(error)}"
        
def test_registration_error_can_be_raised() -> None:
    """# Test that Registration Error can be Raised."""
    # Raise error.
    with raises(RegistrationError) as exc_info: raise RegistrationError("test error")
    
    # Verify message.
    assert str(exc_info.value) == "test error", \
        f"RegistrationError message expected to be 'test error', got {str(exc_info)}"
        

# DUPLICATE ENTRY ERROR ============================================================================

def test_duplicate_entry_error_inheritance() -> None:
    """# Test that Duplicate Entry Error inherits from Registration Error."""
    # Instantiate error.
    error:  DuplicateEntryError =   DuplicateEntryError(
                                        entry_name =    "test_entry",
                                        registry_name = "test_registry"
                                    )
    
    # Ensure inheritance.
    assert isinstance(error, RegistrationError),    \
        f"DuplicateEntryError no longer inherits from RegistrationError"
    assert isinstance(error, Exception),    \
        f"DuplicateEntryError no longer inherits from Exception"
        
def test_duplicate_entry_error_message() -> None:
    """# Test Duplicate Entry Error Formatting."""
    # Instantiate error.
    error:  DuplicateEntryError =   DuplicateEntryError(
                                        entry_name =    "test_entry",
                                        registry_name = "test_registry"
                                    )
    
    # Define expected message.
    message:    str =   """Entry "test_entry" is already registered in test_registry registry"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"DuplicateEntryError message expected to be '{message}', got '{str(error)}'"
        
def test_duplicate_entry_error_message_with_special_characters() -> None:
    """# Test Duplicate Entry Error Formatting with Special Characters."""
    # Instantiate error.
    error:  DuplicateEntryError =   DuplicateEntryError(
                                        entry_name =    "test-entry",
                                        registry_name = "test_registry_123"
                                    )
    
    # Define expected message.
    message:    str =   """Entry "test-entry" is already registered in test_registry_123 registry"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"DuplicateEntryError message expected to be '{message}', got '{str(error)}'"
        
# ENTRY NOT FOUND ERROR ============================================================================

def test_entry_not_found_error_inheritance() -> None:
    """# Test that Entry Not Found Error Inherits from Registration Error."""
    # Instantiate error.
    error:  EntryNotFoundError =    EntryNotFoundError(
                                        entry_name =    "test_entry",
                                        registry_name = "test_registry"
                                    )
    
    # Ensure inheritance.
    assert isinstance(error, RegistrationError),    \
        f"EntryNotFoundError no longer inherits from RegistrationError"
    assert isinstance(error, Exception),    \
        f"EntryNotFoundError no longer inherits from Exception"
        
def test_entry_not_found_error_message() -> None:
    """# Test Duplicate Entry Error Formatting."""
    # Instantiate error.
    error:  EntryNotFoundError =    EntryNotFoundError(
                                        entry_name =    "test_entry",
                                        registry_name = "test_registry"
                                    )
    
    # Define expected message.
    message:    str =   """Entry "test_entry" not registered in test_registry registry"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"EntryNotFoundError message expected to be '{message}', got '{str(error)}'"
        
# ENTRY POINT NOT CONFIGURED ERROR =================================================================

def test_entry_point_not_configured_error_inheritance() -> None:
    """# Test that Entry Point Not Configured Error Inherits from Registration Error."""
    # Instantiate error.
    error:  EntryPointNotConfiguredError =  EntryPointNotConfiguredError(
                                                entry_name =    "test_entry",
                                            )
    
    # Ensure inheritance.
    assert isinstance(error, RegistrationError),    \
        f"EntryPointNotConfiguredError no longer inherits from RegistrationError"
    assert isinstance(error, Exception),    \
        f"EntryPointNotConfiguredError no longer inherits from Exception"
        
def test_entry_point_not_configured_error_message() -> None:
    """# Test Entry Point Not Configured Error Formatting."""
    # Instantiate error.
    error:  EntryPointNotConfiguredError =  EntryPointNotConfiguredError(
                                                entry_name =    "test_entry",
                                            )
    
    # Define expected message.
    message:    str =   """Entry "test_entry" was not registered with an entry point"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"EntryPointNotConfiguredError message expected to be '{message}', got '{str(error)}'"

# PARSER NOT CONFIGURED ERROR ======================================================================

def test_parser_not_configured_error_inheritance() -> None:
    """# Test that Parser Not Configured Error Inherits from Registration Error."""
    # Instantiate error.
    error:  ParserNotConfiguredError =  ParserNotConfiguredError(
                                            entry_name =    "test_entry",
                                        )
    
    # Ensure inheritance.
    assert isinstance(error, RegistrationError),    \
        f"ParserNotConfiguredError no longer inherits from RegistrationError"
    assert isinstance(error, Exception),    \
        f"ParserNotConfiguredError no longer inherits from Exception"
        
def test_parser_point_not_configured_error_message() -> None:
    """# Test Parser Not Configured Error Formatting."""
    # Instantiate error.
    error:  ParserNotConfiguredError =  ParserNotConfiguredError(
                                            entry_name =    "test_entry",
                                        )
    
    # Define expected message.
    message:    str =   """Entry "test_entry" was not registered with an argument parser handler"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"ParserNotConfiguredError message expected to be '{message}', got '{str(error)}'"
        
# REGISTRY NOT LOADED ERROR ========================================================================

def test_register_not_loaded_error_inheritance() -> None:
    """# Test that Register Not Loaded Error Inherits from Registration Error."""
    # Instantiate error.
    error:  RegistryNotLoadedError =    RegistryNotLoadedError(
                                            registry_name = "test_registry",
                                        )
    
    # Ensure inheritance.
    assert isinstance(error, RegistrationError),    \
        f"RegistryNotLoadedError no longer inherits from RegistrationError"
    assert isinstance(error, Exception),    \
        f"RegistryNotLoadedError no longer inherits from Exception"
        
def test_register_not_loaded_error_message() -> None:
    """# Test Register Not Loaded Error Formatting."""
    # Instantiate error.
    error:  RegistryNotLoadedError =    RegistryNotLoadedError(
                                            registry_name = "test_registry",
                                        )
    
    # Define expected message.
    message:    str =   """Operation attempted requires that the test_registry registry is loaded"""
    
    # Ensure that message holds proper format.
    assert str(error) == message,   \
        f"RegistryNotLoadedError message expected to be '{message}', got '{str(error)}'"
        
# GENERIC ==========================================================================================

def test_errors_can_be_caught_generically() -> None:
    """# Test that all Registration Errors can be Caught Generically."""
    # Define exceptions being tested.
    exceptions: List[Tuple[RegistrationError, Tuple[str]]] =    [
        (DuplicateEntryError,           ("test", "test")),
        (EntryNotFoundError,            ("test", "test")),
        (EntryPointNotConfiguredError,  ("test",)),
        (ParserNotConfiguredError,      ("test",)),
        (RegistryNotLoadedError,        ("test",))
    ]
    
    # For each exception...
    for exception_class, args in exceptions:
        
        # Ensure that exception can be caught generically.
        with raises(RegistrationError): raise exception_class(*args)
        
def test_hierarchy() -> None:
    """# Test Exception Hierarchy."""
    # Define a helper function to raise exceptions.
    def handle_error(exception_class, args):
        
        # Raise the exception.
        try:                                    raise exception_class(*args)
        
        # Catch the exception and indicate which one was caught.
        except DuplicateEntryError:             return "duplicate-entry"
        except EntryNotFoundError:              return "entry-not-found"
        except EntryPointNotConfiguredError:    return "entry-point-not-configured"
        except ParserNotConfiguredError:        return "parser-not-configured"
        except RegistryNotLoadedError:          return "registry-not-loaded"
        except RegistrationError:               return "registration-error"
    
    # Ensure that each error is caught before generic registration error.
    assert handle_error(DuplicateEntryError,            ("test", "test"))   == "duplicate-entry",               \
        f"DuplicateEntryError not caught before RegistrationError"
    assert handle_error(EntryNotFoundError,             ("test", "test"))   == "entry-not-found",               \
        f"EntryNotFoundError not caught before RegistrationError"
    assert handle_error(EntryPointNotConfiguredError,   ("test",))          == "entry-point-not-configured",    \
        f"EntryPointNotConfiguredError not caught before RegistrationError"
    assert handle_error(ParserNotConfiguredError,       ("test",))          == "parser-not-configured",    \
        f"ParserNotConfiguredError not caught before RegistrationError"
    assert handle_error(RegistryNotLoadedError,         ("test",))          == "registry-not-loaded",    \
        f"RegistryNotLoadedError not caught before RegistrationError"