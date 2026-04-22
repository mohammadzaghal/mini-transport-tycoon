from __future__ import annotations

from collections.abc import Iterable

from src.enums import TileType
from src.models.tile import Tile

class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._tiles = [
            [Tile(x=x, y=y) for x in range(width)]
            for y in range(height)
        ]
        self.facilities: dict = {}

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Tile:
        if not self.in_bounds(x, y):
            return None
        return self._tiles[y][x]

    def set_tile_type(self, x: int, y: int, tile_type: TileType) -> None:
        tile = self.get_tile(x, y)
        if tile is not None:
            tile.tile_type = tile_type

    def neighbors4(self, x: int, y: int) -> list:
        neighbors = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tile = self.get_tile(x + dx, y + dy)
            if tile is not None:
                neighbors.append(tile)
        return neighbors

    def iter_tiles(self) -> Iterable:
        for row in self._tiles:
            yield from row

    def is_road_buildable(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        if tile.is_city_road:
            return False
        return tile.tile_type in {TileType.GRASS, TileType.FOREST}

    def is_track_buildable(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        if tile.is_entry_point:
            return False
        return tile.tile_type in {TileType.GRASS, TileType.FOREST, TileType.TRACK, TileType.ROAD}