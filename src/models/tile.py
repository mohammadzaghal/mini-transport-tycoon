from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from src.enums import TileType, BridgeType

if TYPE_CHECKING:
    from src.models.stop import Stop
    from src.models.facility import Facility
    from src.models.garage import Garage


@dataclass
class Tile:
    x: int
    y: int
    tile_type: TileType = TileType.GRASS
    tree_count: int = 0
    zone_name: str = ""
    is_bank: bool = False
    is_entry_point: bool = False
    is_route_road: bool = False
    is_stop: bool = False
    is_city_road: bool = False
    bridge_type: Optional[BridgeType] = None
    stop_ref: Optional["Stop"] = field(default=None, repr=False)
    facility_ref: Optional["Facility"] = field(default=None, repr=False)
    garage_ref: Optional["Garage"] = field(default=None, repr=False)
    is_garage: bool = False

    @property
    def is_buildable(self) -> bool:
        if self.is_city_road:
            return False
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.ROAD}

    @property
    def is_track_buildable(self) -> bool:
        if self.is_city_road:
            return False
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.TRACK}

    @property
    def is_driveable(self) -> bool:
        if self.tile_type == TileType.ROAD:
            return True
        if self.tile_type == TileType.WATER and self.bridge_type is not None:
            return True
        return False

    @property
    def is_track_driveable(self) -> bool:
        if self.tile_type == TileType.TRACK:
            return True
        if self.tile_type == TileType.WATER and self.bridge_type == BridgeType.STEEL:
            return True
        return False

    @property
    def is_water(self) -> bool:
        return self.tile_type == TileType.WATER