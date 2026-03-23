from __future__ import annotations

from dataclasses import dataclass, field
import math

from src.enums import CargoType


@dataclass
class Vehicle:
    name: str
    cargo_type: CargoType
    path: list
    speed_tiles_per_second: float = 2.2
    capacity: int = 1
    vdef_name: str = ""
    reward_distance: int = 0
    current_index: int = 0
    x: float = 0.0
    y: float = 0.0
    delivered_legs: int = 0
    revenue_per_leg: int = 0
    color: str = "#f59e0b"
    route_id: int = -1
    _initialized: bool = field(default=False, init=False, repr=False)

    def initialize_position(self) -> None:
        if not self.path:
            return #if no path nothing to init
        self.x, self.y = self.path[0]
        self.current_index = 0
        self._initialized = True


# moves vehicle one frame at a time (is there a more efficient way to do this?)
    def update(self, dt: float) -> bool:
        if not self.path or len(self.path) < 2:
            return False 

            # FOR COLLIDING PATHS - DANA

        if not self._initialized:
            self.initialize_position()

        target_index = (self.current_index + 1) % len(self.path)
        target_x, target_y = self.path[target_index]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < 1e-6:
            self.current_index = target_index
            if self.current_index == 0:
                self.delivered_legs += 1
                return True
            return False

        step = self.speed_tiles_per_second * dt

        if step >= distance:
            self.x = target_x
            self.y = target_y
            self.current_index = target_index
            if self.current_index == 0:
                self.delivered_legs += 1
                return True
            return False

        self.x += (dx / distance) * step
        self.y += (dy / distance) * step
        return False