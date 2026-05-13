from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Garage:
    """A vehicle depot where vehicles are stored, upgraded, and sold.

    Attributes:
        x: Tile column position on the map.
        y: Tile row position on the map.
        capacity: Maximum number of vehicles that can be housed here.
    """

    x: int
    y: int
    capacity: int = 6

    @property
    def pos(self) -> tuple:
        """The (x, y) tile coordinates of this garage as a tuple."""
        return (self.x, self.y)
