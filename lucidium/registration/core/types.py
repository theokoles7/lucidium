"""# lucidium.registration.core.types

Registration components typing.
"""

__all__ =   [
                "EntryType"
            ]

from typing                             import TypeVar

from lucidium.registration.core.entry   import Entry

EntryType = TypeVar(name = "EntryType", bound = Entry)