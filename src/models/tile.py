from dataclasses import dataclass
from src.enums import TileType
from typing import Optional

@dataclass
class Tile:
    x: int
    y: int
    tile_type: TileType = TileType.GRASS
    tree_count: int = 0
    has_stop: bool = False
    zone_name: Optional[str] = None
    @property
    def is_buildable(self) -> bool:
        return self.tile_type in {TileType.GRASS, TileType.FOREST, TileType.ROAD}

    @property
    def is_driveable(self) -> bool:
        return self.tile_type == TileType.ROAD
