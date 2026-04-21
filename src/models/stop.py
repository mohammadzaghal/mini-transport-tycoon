from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from src.enums import CargoType

# Stop class: player-built structure for cargo delivery and pickup
@dataclass
class Stop:
    id: int
    x: int
    y: int
    zone_name: str = ""
    inventory: Dict[CargoType, float] = field(default_factory=dict)

    def take(self, cargo: CargoType, amount: float) -> float:
        available = self.inventory.get(cargo, 0.0)
        taken = min(available, amount)
        self.inventory[cargo] = available - taken
        return taken

    def deposit(self, cargo: CargoType, amount: float) -> None:
        self.inventory[cargo] = self.inventory.get(cargo, 0.0) + amount

    def stock(self, cargo: CargoType) -> float:
        return self.inventory.get(cargo, 0.0)

    def total_stock(self) -> float:
        return sum(self.inventory.values())