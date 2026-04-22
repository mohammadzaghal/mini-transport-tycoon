from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from src.enums import CargoType, FacilityType
from src.config import FACILITY_DEFS, FACILITY_MAX_STOCK


# this is the facility class (mines, fuel rigs etc)
# basically a building that makes stuff over time
@dataclass
class Facility:
    name: str
    fac_type: FacilityType  # what kind of facility (ore mine, fuel gas smtg..)
    x: int
    y: int

    # dict of cargo -> how much we have rn
    inventory: Dict[CargoType, float] = field(default_factory=dict)
    _accum: Dict[CargoType, float] = field(default_factory=dict, init=False, repr=False)  # not rly used i think??

    def __post_init__(self) -> None:
        # runs right after the dataclass is made
        # just sets up the inventory dict with 0 for everything this facility cares about
        defs = FACILITY_DEFS.get(self.fac_type, {})
        for cargo in defs.get("produces", {}):
            self.inventory.setdefault(cargo, 0.0)  # start at 0 if not already there
        for cargo in defs.get("consumes", {}):
            self.inventory.setdefault(cargo, 0.0)

    # this gets called every frame (well sim tick)
    # sim_dt = how much game time passed since last tick
    def tick(self, sim_dt: float) -> None:
        defs = FACILITY_DEFS.get(self.fac_type, {})
        consumes = defs.get("consumes", {})  # stuff it needs to eat
        produces = defs.get("produces", {})  # stuff it makes

        # FIRST check if we have enough of everything we need
        # if even 1 ingredient is missing we bail out (no half recipies)
        if consumes:
            for cargo, rate in consumes.items():
                needed = rate * sim_dt  # rate is per sec, times dt = amount for this tick
                if self.inventory.get(cargo, 0.0) < needed:
                    return  # not enough, skip this tick

        # ok we got enough, actualy subtract the inputs now
        for cargo, rate in consumes.items():
            self.inventory[cargo] = max(0.0, self.inventory.get(cargo, 0.0) - rate * sim_dt)
            # max 0 just incase floating point makes it slightly negative

        # now add the outputs (but dont go past max stock or it overflows 4ever)
        for cargo, rate in produces.items():
            current = self.inventory.get(cargo, 0.0)
            if current < FACILITY_MAX_STOCK:  # only make more if theres room
                self.inventory[cargo] = min(FACILITY_MAX_STOCK, current + rate * sim_dt)

    # called when a truck/train pulls up and wants to load cargo
    # returns how much it actually got (maybe less than asked if low stock)
    def give(self, cargo: CargoType, amount: float) -> float:
        available = self.inventory.get(cargo, 0.0)
        taken = min(available, amount)  # cant give more then we have duh
        self.inventory[cargo] = available - taken
        return taken

    # opposite of give, vehicle drops stuff off here
    def receive(self, cargo: CargoType, amount: float) -> None:
        current = self.inventory.get(cargo, 0.0)
        self.inventory[cargo] = min(FACILITY_MAX_STOCK, current + amount)  # cap at max

    # just a getter basically, how much of X do we have
    def stock(self, cargo: CargoType) -> float:
        return self.inventory.get(cargo, 0.0)

    # these 2 @property things just pull from the config so u dont have to type
    # FACILITY_DEFS[...][...] everywhere. makes it look like an attribute
    @property
    def produces(self) -> Dict[CargoType, float]:
        return FACILITY_DEFS.get(self.fac_type, {}).get("produces", {})

    @property
    def consumes(self) -> Dict[CargoType, float]:
        return FACILITY_DEFS.get(self.fac_type, {}).get("consumes", {})
