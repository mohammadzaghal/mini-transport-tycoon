from __future__ import annotations

from enum import Enum


class TileType(Enum):
    GRASS = "grass"
    FOREST = "forest"
    ROAD = "road"
    CITY = "city"
    FACILITY = "facility"


class CargoType(Enum):
    PASSENGERS = "Passengers"


class TimeSpeed(Enum):
    PAUSE = 0
    NORMAL = 1
    FAST = 2
    VERY_FAST = 4


class Tool(Enum):
    NONE = "none"
    ROAD = "road"
    ROUTE_P1 = "route_p1"
    ROUTE_P2 = "route_p2"
    VEHICLES = "vehicles"
    DEPLOY_VEHICLE_P1 = "deploy_vehicle_p1"
    DEPLOY_VEHICLE_P2 = "deploy_vehicle_p2"
    BULLDOZE = "bulldoze"