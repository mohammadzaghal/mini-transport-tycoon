from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from src.enums import CargoType, FacilityType
from src.config import FACILITY_DEFS, FACILITY_MAX_STOCK


@dataclass
class Facility:
    """A production building (mine, rig, dome, etc.) that generates cargo over time.

    Each facility type is defined in ``FACILITY_DEFS`` and specifies what cargo
    it consumes and produces per simulated second.  A facility will only produce
    output when it has sufficient input stock to cover the current tick.

    Attributes:
        name: Human-readable name shown on the map tooltip.
        fac_type: The FacilityType enum value that selects this facility's
            production recipe from FACILITY_DEFS.
        x: Tile column position of the facility's footprint anchor.
        y: Tile row position of the facility's footprint anchor.
        inventory: Current stock of each cargo type held by this facility.
    """

    name: str
    fac_type: FacilityType
    x: int
    y: int

    inventory: Dict[CargoType, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialise the inventory with zero stock for all produced and consumed cargo types."""
        defs = FACILITY_DEFS.get(self.fac_type, {})
        for cargo in defs.get("produces", {}):
            self.inventory.setdefault(cargo, 0.0)
        for cargo in defs.get("consumes", {}):
            self.inventory.setdefault(cargo, 0.0)

    def tick(self, sim_dt: float) -> None:
        """Advance the production cycle by one simulation time step.

        Consumes input cargo and produces output cargo proportionally to
        ``sim_dt``.  If any required input is insufficient the entire tick is
        skipped so partial recipes never occur.  Output is capped at
        ``FACILITY_MAX_STOCK`` to prevent unbounded accumulation.

        Args:
            sim_dt: Elapsed simulated time in seconds since the last tick.
        """
        defs = FACILITY_DEFS.get(self.fac_type, {})
        consumes = defs.get("consumes", {})
        produces = defs.get("produces", {})

        if consumes:
            for cargo, rate in consumes.items():
                needed = rate * sim_dt
                if self.inventory.get(cargo, 0.0) < needed:
                    return

        for cargo, rate in consumes.items():
            self.inventory[cargo] = max(0.0, self.inventory.get(cargo, 0.0) - rate * sim_dt)

        for cargo, rate in produces.items():
            current = self.inventory.get(cargo, 0.0)
            if current < FACILITY_MAX_STOCK:
                self.inventory[cargo] = min(FACILITY_MAX_STOCK, current + rate * sim_dt)

    def give(self, cargo: CargoType, amount: float) -> float:
        """Transfer up to ``amount`` units of a cargo type out of this facility.

        Args:
            cargo: The cargo type the vehicle wants to collect.
            amount: Maximum units requested.

        Returns:
            The actual amount transferred, limited by the current stock.
        """
        available = self.inventory.get(cargo, 0.0)
        taken = min(available, amount)
        self.inventory[cargo] = available - taken
        return taken

    def receive(self, cargo: CargoType, amount: float) -> None:
        """Accept a delivery of cargo into this facility's inventory.

        The stored amount is capped at ``FACILITY_MAX_STOCK`` to prevent
        unbounded accumulation.

        Args:
            cargo: The cargo type being delivered.
            amount: Number of units to add.
        """
        current = self.inventory.get(cargo, 0.0)
        self.inventory[cargo] = min(FACILITY_MAX_STOCK, current + amount)

    def stock(self, cargo: CargoType) -> float:
        """Return the current stock level for one cargo type.

        Args:
            cargo: The cargo type to query.

        Returns:
            Units currently in inventory, or 0.0 if none.
        """
        return self.inventory.get(cargo, 0.0)

    @property
    def produces(self) -> Dict[CargoType, float]:
        """Mapping of cargo type to production rate (units per simulated second) for this facility."""
        return FACILITY_DEFS.get(self.fac_type, {}).get("produces", {})

    @property
    def consumes(self) -> Dict[CargoType, float]:
        """Mapping of cargo type to consumption rate (units per simulated second) for this facility."""
        return FACILITY_DEFS.get(self.fac_type, {}).get("consumes", {})
