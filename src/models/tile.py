from __future__ import annotations

from dataclasses import dataclass

from src.enums import TileType


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

    @property
    def is_buildable(self) -> bool:
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.ROAD}

    @property
    def is_driveable(self) -> bool:
        return self.tile_type == TileType.ROAD