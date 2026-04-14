from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict, Optional

from src.enums import CargoType, VehicleType


@dataclass
class Vehicle:
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
        if not self.path:
            return
        self.x, self.y = self.path[0]
        self.current_index = 0
        self._initialized = True
        self.at_stop = False

    def update(self, dt: float) -> bool:
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
        current_load = sum(self.cargo_on_board.values())
        space = self.capacity - current_load
        to_load = min(space, amount)

        if to_load > 0:
            self.cargo_on_board[cargo] = self.cargo_on_board.get(cargo, 0.0) + to_load

        return to_load

    def unload_all(self) -> Dict[CargoType, float]:
        unloaded = dict(self.cargo_on_board)
        self.cargo_on_board.clear()
        return unloaded

    def unload(self, cargo: CargoType) -> float:
        return self.cargo_on_board.pop(cargo, 0.0)

    @property
    def total_cargo(self) -> float:
        return sum(self.cargo_on_board.values())