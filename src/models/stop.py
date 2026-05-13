from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from src.enums import CargoType

@dataclass
class Stop:
    """A player-built waypoint where vehicles load and unload cargo or passengers.

    Attributes:
        id: Unique integer identifier for this stop.
        x: Tile column position on the map.
        y: Tile row position on the map.
        zone_name: Name of the city or zone this stop serves, if any.
        inventory: Current stock of each cargo type waiting at this stop.
    """

    id: int
    x: int
    y: int
    zone_name: str = ""
    inventory: Dict[CargoType, float] = field(default_factory=dict)

    def take(self, cargo: CargoType, amount: float) -> float:
        """Remove up to ``amount`` units of a cargo type from the stop's inventory.

        Args:
            cargo: The cargo type to remove.
            amount: Maximum units to take.

        Returns:
            The actual amount taken, which may be less than ``amount`` when
            the stop does not have sufficient stock.
        """
        available = self.inventory.get(cargo, 0.0)
        taken = min(available, amount)
        self.inventory[cargo] = available - taken
        return taken

    def deposit(self, cargo: CargoType, amount: float) -> None:
        """Add units of a cargo type to the stop's inventory.

        Args:
            cargo: The cargo type to add.
            amount: Number of units to deposit.
        """
        self.inventory[cargo] = self.inventory.get(cargo, 0.0) + amount

    def stock(self, cargo: CargoType) -> float:
        """Return the current stock level of one cargo type.

        Args:
            cargo: The cargo type to query.

        Returns:
            The number of units currently held, or 0.0 if none.
        """
        return self.inventory.get(cargo, 0.0)

    def total_stock(self) -> float:
        """Return the total number of cargo units across all types in inventory."""
        return sum(self.inventory.values())