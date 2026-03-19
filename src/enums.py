from enum import Enum


class TileType(Enum):
    GRASS = "grass"
    FOREST = "forest"
    WATER = "water"
    ROAD = "road"
    CITY = "city"
    FACILITY = "facility"


class CargoType(Enum):
    PASSENGERS = "Passengers"
    WOOD = "Wood"
    IRON = "Iron"
    FOOD = "Food"


class TimeSpeed(Enum):
    PAUSE = 0
    NORMAL = 1
    FAST = 2
    VERY_FAST = 4


class Tool(Enum):
    ROAD = "Road"
    STOP = "Stop"
    BULLDOZE = "Bulldoze"
    BUS = "Spawn Bus"
    NONE = "Cancel"
