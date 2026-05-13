from __future__ import annotations

from enum import Enum


class TileType(Enum):
    """The terrain or infrastructure type of a single map tile."""

    GRASS    = "grass"     # Open, buildable land
    FOREST   = "forest"    # Tree-covered land; costs extra to clear
    ROAD     = "road"      # Player-built or city road; driveable by wheeled vehicles
    TRACK    = "track"     # Player-built rail; driveable by maglev only
    CITY     = "city"      # City building block; not directly buildable
    FACILITY = "facility"  # Industrial facility footprint tile
    WATER    = "water"     # Impassable unless bridged


class CargoType(Enum):
    """The type of goods or resources that can be transported."""

    IRON_ORE     = "Iron Ore"      # Basic ore produced by ore mines
    ALLOY_ORE    = "Alloy Ore"     # Mid-tier ore produced by ore mines
    TITANIUM_ORE = "Titanium Ore"  # High-value ore produced by ore mines
    FUEL         = "Fuel"          # Energy resource produced by fuel rigs
    AQUATICS     = "Aquatics"      # Water supply produced by aqua domes
    CRYSTALS     = "Crystals"      # Rare material produced by crystal labs


class FacilityType(Enum):
    """The production category of an industrial facility."""

    ORE_MINE    = "Ore Mine"      # Produces iron, alloy, and titanium ores
    FUEL_RIG    = "Fuel Rig"      # Produces fuel
    AQUA_DOME   = "Aqua Dome"     # Produces aquatics (water supply)
    CRYSTAL_LAB = "Crystal Lab"   # Produces crystals


class VehicleType(Enum):
    """The class of vehicle, which determines which infrastructure it can use."""

    BUS   = "Rover"   # Wheeled bus for road routes; carries passengers
    TRUCK = "Hauler"  # Wheeled truck for road routes; carries cargo
    TRAIN = "Maglev"  # Rail vehicle for track routes; high-capacity bulk cargo


class BridgeType(Enum):
    """The structural level of a bridge built over a water tile."""

    WOODEN = "Wooden"  # Level 1 — trucks only; paid with iron ore
    STONE  = "Stone"   # Level 2 — trucks and buses; paid with alloy ore
    STEEL  = "Steel"   # Level 3 — all vehicles including maglev; paid with titanium ore


class TimeSpeed(Enum):
    """The simulation speed multiplier applied to the game world."""

    PAUSE     = 0  # Simulation frozen; no updates run
    NORMAL    = 1  # Real-time simulation
    FAST      = 2  # 2× accelerated simulation
    VERY_FAST = 4  # 4× accelerated simulation


class Tool(Enum):
    """The currently active player action tool selected from the HUD."""

    NONE              = "none"               # No tool selected; cursor is passive
    ROAD              = "road"               # Click tiles to build roads
    TRACK             = "track"              # Click tiles to build rail tracks
    ROUTE_P1          = "route_p1"           # Waiting for first route endpoint click
    ROUTE_P2          = "route_p2"           # Waiting for second route endpoint click
    VEHICLES          = "vehicles"           # Vehicle purchase panel open
    DEPLOY_VEHICLE_P1 = "deploy_vehicle_p1"  # Waiting for first deploy endpoint
    DEPLOY_VEHICLE_P2 = "deploy_vehicle_p2"  # Waiting for second deploy endpoint
    BULLDOZE          = "bulldoze"           # Click tiles to remove infrastructure
    STOP              = "stop"               # Click road/track to place a stop
    BRIDGE            = "bridge"             # Click water tiles to build bridges
    GARAGE            = "garage"             # Click grass to build a vehicle garage