from __future__ import annotations

from dataclasses import dataclass, field

from src.enums import TileType, BridgeType

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.stop import Stop
    from src.models.facility import Facility
    from src.models.garage import Garage

@dataclass
class Tile:
    """A single cell in the game map grid.

    Attributes:
        x: Column index of this tile in the grid.
        y: Row index of this tile in the grid.
        tile_type: The terrain or infrastructure type (GRASS, WATER, ROAD, etc.).
        tree_count: Number of trees on this tile; used for forest density.
        zone_name: Name of the city or zone this tile belongs to, if any.
        is_bank: True when this tile contains a bank building.
        is_entry_point: True when this tile is a facility's designated entry/exit.
        is_route_road: True when a player-defined route passes through here.
        is_stop: True when a cargo/passenger stop has been built on this tile.
        is_city_road: True when the tile is part of a procedurally generated city road.
        bridge_type: The bridge level installed on a WATER tile, or None if unbridged.
        stop_ref: Reference to the Stop object placed on this tile, or None.
        facility_ref: Reference to the Facility object on this tile, or None.
        garage_ref: Reference to the Garage object on this tile, or None.
        is_garage: True when a vehicle garage has been built here.
    """

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
        """True when a road or stop can be built on this tile.

        City road tiles are excluded even when their terrain would otherwise allow it.
        """
        if self.is_city_road:
            return False
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.ROAD}

    @property
    def is_track_buildable(self) -> bool:
        """True when a rail track can be built on this tile.

        City road tiles are excluded even when their terrain would otherwise allow it.
        """
        if self.is_city_road:
            return False
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.TRACK}

    @property
    def is_driveable(self) -> bool:
        """True when wheeled vehicles (buses, trucks) can traverse this tile.

        ROAD tiles are always driveable.  WATER tiles are driveable only when
        a bridge of any type has been installed.
        """
        if self.tile_type == TileType.ROAD:
            return True
        if self.tile_type == TileType.WATER and self.bridge_type is not None:
            return True
        return False

    @property
    def is_track_driveable(self) -> bool:
        """True when rail vehicles (maglev) can traverse this tile.

        TRACK tiles are always track-driveable.  WATER tiles are track-driveable
        only when a STEEL bridge has been installed.
        """
        if self.tile_type == TileType.TRACK:
            return True
        if self.tile_type == TileType.WATER and self.bridge_type == BridgeType.STEEL:
            return True
        return False

    @property
    def is_water(self) -> bool:
        """True when this tile's terrain is WATER."""
        return self.tile_type == TileType.WATER