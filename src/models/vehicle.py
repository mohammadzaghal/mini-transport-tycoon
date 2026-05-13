from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict, Optional

from src.enums import CargoType, VehicleType


@dataclass
class Vehicle:
    """An autonomous vehicle that moves along a route carrying cargo or passengers.

    Attributes:
        name: Display name of this vehicle.
        vehicle_type: Classification (bus, truck, or train) that determines
            which road/track type it can use.
        path: Ordered list of (x, y) tile coordinates forming the route loop.
        speed_tiles_per_second: Movement speed in tiles per real-time second.
        capacity: Maximum total cargo units this vehicle can carry.
        base_speed: Original speed before any upgrades.
        base_capacity: Original capacity before any upgrades.
        level: Current upgrade level (starts at 1).
        vdef_name: Key into VEHICLE_DEFS config used for this vehicle.
        reward_distance: Accumulated tile distance used in revenue calculations.
        current_index: Index into ``path`` pointing to the next target tile.
        x: Current fractional tile x-position.
        y: Current fractional tile y-position.
        delivered_legs: Number of complete route loops the vehicle has finished.
        revenue_per_leg: Money earned each time the vehicle completes one loop.
        color: Hex colour string used when rendering this vehicle on the map.
        route_id: ID of the Route this vehicle is assigned to, or -1 if none.
        cargo_on_board: Mapping of CargoType to current load amount.
        age_days: Total simulated days this vehicle has been in service.
        maintenance_timer: Accumulated days since the last maintenance event.
        needs_maintenance: True when maintenance is overdue.
        maintenance_due_days: Interval in simulated days between maintenance events.
        returning_to_garage: True when the vehicle has been recalled to its garage.
        garage_path: Path tiles to follow when returning to the garage.
        garage_index: Current progress index into ``garage_path``.
    """

    name: str
    vehicle_type: VehicleType  # bus / truck / train
    path: list  # list of (x, y) tiles the vehicle follows
    speed_tiles_per_second: float = 2.2
    capacity: int = 1  # max cargo capacity (can change with upgrades)

    base_speed: float = 0.0
    base_capacity: int = 0
    level: int = 1  # upgrade level
    vdef_name: str = ""

    reward_distance: int = 0  # used for calculating rewards (money/oil)
    current_index: int = 0

    x: float = 0.0
    y: float = 0.0

    delivered_legs: int = 0  # number of completed route loops
    revenue_per_leg: int = 0  # money earned per completed loop

    color: str = "#f59e0b"
    route_id: int = -1

    cargo_on_board: Dict[CargoType, float] = field(default_factory=dict)  # current cargo

    age_days: float = 0.0
    maintenance_timer: float = 0.0
    needs_maintenance: bool = False
    maintenance_due_days: float = 30.0

    returning_to_garage: bool = False
    garage_path: list = field(default_factory=list)
    garage_index: int = 0

    _initialized: bool = field(default=False, init=False, repr=False)

    at_stop: bool = field(default=False, init=False, repr=False)
    _prev_index: int = field(default=0, init=False, repr=False)

    def initialize_position(self) -> None:
        """Snap the vehicle to the first tile in its path and reset movement state.

        Does nothing if ``path`` is empty.
        """
        if not self.path:
            return
        self.x, self.y = self.path[0]
        self.current_index = 0
        self._initialized = True
        self.at_stop = False

    def update(self, dt: float) -> bool:
        """Advance the vehicle along its path by one simulation tick.

        Moves the vehicle toward the next tile at the current speed.  When the
        vehicle reaches the end of the path and wraps back to index 0 it
        increments ``delivered_legs`` and returns True, signalling that a full
        loop has been completed.

        Args:
            dt: Elapsed real time in seconds since the last call.

        Returns:
            True if the vehicle just completed a full route loop, False otherwise.
        """
        if not self.path or len(self.path) < 2:
            return False

        if not self._initialized:
            self.initialize_position()

        self.at_stop = False
        self._prev_index = self.current_index  # track previous tile index

        target_index = (self.current_index + 1) % len(self.path)
        target_x, target_y = self.path[target_index]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)  # straight-line distance

        if distance < 1e-6:
            self.current_index = target_index
            if self.current_index == 0:
                self.delivered_legs += 1
                return True
            return False

        step = self.speed_tiles_per_second * dt

        if step >= distance:
            self.x = float(target_x)
            self.y = float(target_y)

            old_index = self.current_index
            self.current_index = target_index

            if self.current_index != old_index:
                self.at_stop = True  # reached a node/tile

            if self.current_index == 0:
                self.delivered_legs += 1
                return True
            return False

        self.x += (dx / distance) * step
        self.y += (dy / distance) * step
        return False

    def load(self, cargo: CargoType, amount: float) -> float:
        """Load as much of a cargo type as the vehicle's free capacity allows.

        Args:
            cargo: The cargo type to load.
            amount: The desired amount to load.

        Returns:
            The actual amount loaded, which may be less than ``amount`` if the
            vehicle does not have sufficient free capacity.
        """
        current_load = sum(self.cargo_on_board.values())
        space = self.capacity - current_load
        to_load = min(space, amount)

        if to_load > 0:
            self.cargo_on_board[cargo] = self.cargo_on_board.get(cargo, 0.0) + to_load

        return to_load

    def unload_all(self) -> Dict[CargoType, float]:
        """Remove and return all cargo currently on board.

        Returns:
            A dictionary mapping each carried CargoType to its amount.
            The vehicle's ``cargo_on_board`` is empty after this call.
        """
        unloaded = dict(self.cargo_on_board)
        self.cargo_on_board.clear()
        return unloaded

    def unload(self, cargo: CargoType) -> float:
        """Remove and return the entire load of one cargo type.

        Args:
            cargo: The cargo type to remove.

        Returns:
            The amount that was on board, or 0.0 if none was carried.
        """
        return self.cargo_on_board.pop(cargo, 0.0)

    @property
    def total_cargo(self) -> float:
        """Total number of cargo units currently on board across all types."""
        return sum(self.cargo_on_board.values())