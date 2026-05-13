"""Game-wide configuration constants.

This module centralises all tunable parameters for the Mini Transport Tycoon
simulation.  Adjust values here to change game balance, map dimensions, UI
layout, vehicle stats, facility production rates, and bridge costs without
touching logic code.
"""

from src.enums import CargoType, FacilityType, BridgeType, VehicleType

WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 700
TOP_BAR_HEIGHT    = 0
BOTTOM_BAR_HEIGHT = 100

TILE_SIZE  = 32
MAP_WIDTH  = 80
MAP_HEIGHT = 55

PANEL_BG     = "#120805"
PANEL_ACCENT = "#2a1008"
HUD_TEXT     = "#f0e6d0"
BACKGROUND   = "#0a0604"
GRID_LINE    = "#1a1208"

ROAD_COST         = 100
TRACK_COST        = 150
FOREST_CLEAR_COST = 50
GARAGE_COST       = 2000
STARTING_MONEY    = 20000

BRIDGE_ORE_COSTS = {
    BridgeType.WOODEN: (CargoType.IRON_ORE,     10),
    BridgeType.STONE:  (CargoType.ALLOY_ORE,    10),
    BridgeType.STEEL:  (CargoType.TITANIUM_ORE, 10),
}

BRIDGE_SPEED_LIMITS = {
    BridgeType.WOODEN: 1.5,
    BridgeType.STONE:  2.5,
    BridgeType.STEEL:  99.0,
}

BRIDGE_VEHICLE_SUPPORT = {
    BridgeType.WOODEN: {"bus": False, "truck": True,  "train": False},
    BridgeType.STONE:  {"bus": True,  "truck": True,  "train": False},
    BridgeType.STEEL:  {"bus": True,  "truck": True,  "train": True},
}

TICK_MS = 50

MAINTENANCE_INTERVAL_DAYS = 30
MAINTENANCE_BASE_COST     = 200
GAME_SECONDS_PER_DAY      = 60

CITY_GROWTH_POINTS_PER_DELIVERY = 10
CITY_GROWTH_THRESHOLD           = 200

PASSENGER_FARE = 5

CARGO_PRICE = {
    CargoType.IRON_ORE:     5,
    CargoType.ALLOY_ORE:    10,
    CargoType.TITANIUM_ORE: 20,
    CargoType.FUEL:         6,
    CargoType.AQUATICS:     12,
    CargoType.CRYSTALS:     10,
}

FACILITY_DEFS = {
    FacilityType.ORE_MINE: {
        "produces": {CargoType.IRON_ORE: 0.35, CargoType.ALLOY_ORE: 0.2, CargoType.TITANIUM_ORE: 0.1},
        "consumes": {},
    },
    FacilityType.FUEL_RIG: {
        "produces": {CargoType.FUEL: 0.4},
        "consumes": {},
    },
    FacilityType.AQUA_DOME: {
        "produces": {CargoType.AQUATICS: 0.35},
        "consumes": {},
    },
    FacilityType.CRYSTAL_LAB: {
        "produces": {CargoType.CRYSTALS: 0.45},
        "consumes": {},
    },
}

FACILITY_NAME_TO_TYPE = {
    "North Mine":  FacilityType.ORE_MINE,
    "South Mine":  FacilityType.ORE_MINE,
    "Fuel Rig":    FacilityType.FUEL_RIG,
    "Aqua Dome N": FacilityType.AQUA_DOME,
    "Aqua Dome E": FacilityType.AQUA_DOME,
    "Aqua Dome S": FacilityType.AQUA_DOME,
    "Crystal Lab": FacilityType.CRYSTAL_LAB,
}

FACILITY_MAX_STOCK = 200

CITY_DEMAND_TYPES = [
    CargoType.IRON_ORE, CargoType.ALLOY_ORE, CargoType.TITANIUM_ORE,
    CargoType.FUEL, CargoType.AQUATICS, CargoType.CRYSTALS,
]

VEHICLE_DEFS = [
    {
        "name": "Rover",
        "cost": 1200,
        "speed": 3.2,
        "capacity": 35,
        "color": "#7ed636",
        "vehicle_type": VehicleType.BUS,
        "desc": "Road — passengers",
        "maintenance_cost": 300,
    },
    {
        "name": "Hauler",
        "cost": 800,
        "speed": 1.5,
        "capacity": 25,
        "color": "#50c8f5",
        "vehicle_type": VehicleType.TRUCK,
        "desc": "Road — cargo",
        "maintenance_cost": 250,
    },
    {
        "name": "Maglev",
        "cost": 2500,
        "speed": 2.0,
        "capacity": 60,
        "color": "#e06020",
        "vehicle_type": VehicleType.TRAIN,
        "desc": "Rail — bulk cargo",
        "maintenance_cost": 500,
    },
]


VEHICLE_LEVEL_DEFS = {
    VehicleType.BUS: {
        2: {"oil": 50,  "speed_mult": 1.25, "cap_mult": 1.30},
        3: {"oil": 150, "speed_mult": 1.25, "cap_mult": 1.30},
    },
    VehicleType.TRUCK: {
        2: {"oil": 75,  "speed_mult": 1.25, "cap_mult": 1.30},
        3: {"oil": 200, "speed_mult": 1.25, "cap_mult": 1.30},
    },
    VehicleType.TRAIN: {
        2: {"oil": 100, "speed_mult": 1.25, "cap_mult": 1.30},
        3: {"oil": 300, "speed_mult": 1.25, "cap_mult": 1.30},
    },
}
