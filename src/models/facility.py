from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from src.enums import CargoType, FacilityType
from src.config import FACILITY_DEFS, FACILITY_MAX_STOCK


@dataclass
class Facility:
    name: str
    fac_type: FacilityType
    x: int
    y: int

    inventory: Dict[CargoType, float] = field(default_factory=dict)
    _accum: Dict[CargoType, float] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        defs = FACILITY_DEFS.get(self.fac_type, {})
        for cargo in defs.get("produces", {}):
            self.inventory.setdefault(cargo, 0.0)
        for cargo in defs.get("consumes", {}):
            self.inventory.setdefault(cargo, 0.0)

    def tick(self, sim_dt: float) -> None:
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
        available = self.inventory.get(cargo, 0.0)
        taken = min(available, amount)
        self.inventory[cargo] = available - taken
        return taken

    def receive(self, cargo: CargoType, amount: float) -> None:
        current = self.inventory.get(cargo, 0.0)
        self.inventory[cargo] = min(FACILITY_MAX_STOCK, current + amount)

    def stock(self, cargo: CargoType) -> float:
        return self.inventory.get(cargo, 0.0)

    @property
    def produces(self) -> Dict[CargoType, float]:
        return FACILITY_DEFS.get(self.fac_type, {}).get("produces", {})

    @property
    def consumes(self) -> Dict[CargoType, float]:
        return FACILITY_DEFS.get(self.fac_type, {}).get("consumes", {})