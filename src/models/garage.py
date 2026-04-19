from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Garage:
    x: int
    y: int
    capacity: int = 6

    @property
    def pos(self) -> tuple:
        return (self.x, self.y)
