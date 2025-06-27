"""# lucidium.environments.tic_tac_toe.components.glyphs

This module provides the glyphs for the Tic Tac Toe environment in the Lucidium framework.
"""

__all__ = ["Glyphs"]

from enum   import Enum

class Glyphs(Enum):
    """Glyphs for Tic Tac Toe Environment

    This enumeration defines the glyphs used to represent the Tic Tac Toe environment.
    """
    
    EMPTY = " "
    X     = "X"
    O     = "O"
    
    def __str__(self) -> str:
        """Return the string representation of the glyph."""
        return self.value