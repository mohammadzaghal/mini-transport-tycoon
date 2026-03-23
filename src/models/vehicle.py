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
