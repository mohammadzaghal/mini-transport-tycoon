from __future__ import annotations

from enum import Enum


class TileType(Enum):
    GRASS    = "grass"
    FOREST   = "forest"
    ROAD     = "road"
    TRACK    = "track"
    CITY     = "city"
    FACILITY = "facility"
    WATER    = "water"


class CargoType(Enum):
    IRON_ORE     = "Iron Ore"
    ALLOY_ORE    = "Alloy Ore"
    TITANIUM_ORE = "Titanium Ore"
    FUEL         = "Fuel"
    AQUATICS     = "Aquatics"
    CRYSTALS     = "Crystals"


class FacilityType(Enum):
    ORE_MINE    = "Ore Mine"
    FUEL_RIG    = "Fuel Rig"
    AQUA_DOME   = "Aqua Dome"
    CRYSTAL_LAB = "Crystal Lab"


class VehicleType(Enum):
    BUS   = "Rover"
    TRUCK = "Hauler"
    TRAIN = "Maglev"


class BridgeType(Enum):
    WOODEN = "Wooden"
    STONE  = "Stone"
    STEEL  = "Steel"


class TimeSpeed(Enum):
    PAUSE     = 0
    NORMAL    = 1
    FAST      = 2
    VERY_FAST = 4


class Tool(Enum):
    NONE              = "none"
    ROAD              = "road"
    TRACK             = "track"
    ROUTE_P1          = "route_p1"
    ROUTE_P2          = "route_p2"
    VEHICLES          = "vehicles"
    DEPLOY_VEHICLE_P1 = "deploy_vehicle_p1"
    DEPLOY_VEHICLE_P2 = "deploy_vehicle_p2"
    BULLDOZE          = "bulldoze"
    STOP              = "stop"
    BRIDGE            = "bridge"
    GARAGE            = "garage"