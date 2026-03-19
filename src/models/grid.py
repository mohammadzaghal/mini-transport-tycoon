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

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Tile | None:
        if not self.in_bounds(x, y):
            return None
        return self._tiles[y][x]

    def set_tile_type(self, x: int, y: int, tile_type: TileType) -> None:
        tile = self.get_tile(x, y)
        if tile is not None:
            tile.tile_type = tile_type

    def neighbors4(self, x: int, y: int) -> list[Tile]:
        neighbors: list[Tile] = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tile = self.get_tile(x + dx, y + dy)
            if tile is not None:
                neighbors.append(tile)
        return neighbors

    def iter_tiles(self) -> Iterable[Tile]:
        for row in self._tiles:
            yield from row

    def is_road_buildable(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        return tile.tile_type in {TileType.GRASS, TileType.FOREST}

    def is_stop_buildable(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        if tile is None or tile.has_stop:
            return False
        if tile.tile_type in {TileType.WATER, TileType.CITY, TileType.FACILITY}:
            return False
        if tile.tile_type == TileType.ROAD:
            return True
        if tile.tile_type in {TileType.GRASS, TileType.FOREST}:
            return any(neighbor.tile_type == TileType.ROAD for neighbor in self.neighbors4(x, y))
        return False
