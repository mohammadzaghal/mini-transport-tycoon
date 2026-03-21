import random
from src.enums import TileType
from src.models.grid import Grid
from src.models.stop import Stop

class MapGenerator:
    def __init__(self, seed: int = 7) -> None:
        self.random = random.Random(seed)

    def generate(self, grid: Grid) -> list[Stop]:
        self._scatter_forests(grid)
        self._add_lake(grid)
        self._place_zone(grid, 5, 5, 4, 4, TileType.CITY, "North City")
        self._place_zone(grid, 30, 18, 5, 5, TileType.CITY, "South City")
        self._place_zone(grid, 37, 5, 3, 3, TileType.FACILITY, "Iron Mine")
        self._place_zone(grid, 8, 23, 3, 3, TileType.FACILITY, "Forest Camp")
        self._build_demo_roads(grid)
        return self._create_demo_stops(grid)

    def _scatter_forests(self, grid: Grid) -> None:
        for tile in grid.iter_tiles():
            roll = self.random.random()
            if roll < 0.12:
                tile.tile_type = TileType.FOREST
                tile.tree_count = self.random.randint(1, 4)

    def _add_lake(self, grid: Grid) -> None:
        cx, cy = 20, 10
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 5, cx + 6):
                tile = grid.get_tile(x, y)
                if tile is None:
                    continue
                if ((x - cx) ** 2) / 25 + ((y - cy) ** 2) / 9 <= 1.0:
                    tile.tile_type = TileType.WATER
                    tile.tree_count = 0

    def _place_zone(
        self,
        grid: Grid,
        start_x: int,
        start_y: int,
        width: int,
        height: int,
        tile_type: TileType,
        zone_name: str,
    ) -> None:
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                tile = grid.get_tile(x, y)
                if tile is None:
                    continue
                tile.tile_type = tile_type
                tile.zone_name = zone_name
                tile.tree_count = 0

    def _road_line(self, grid: Grid, x1: int, y1: int, x2: int, y2: int) -> None:
        if x1 == x2:
            y_start, y_end = sorted((y1, y2))
            for y in range(y_start, y_end + 1):
                tile = grid.get_tile(x1, y)
                if tile and tile.tile_type not in {TileType.CITY, TileType.FACILITY, TileType.WATER}:
                    tile.tile_type = TileType.ROAD
        elif y1 == y2:
            x_start, x_end = sorted((x1, x2))
            for x in range(x_start, x_end + 1):
                tile = grid.get_tile(x, y1)
                if tile and tile.tile_type not in {TileType.CITY, TileType.FACILITY, TileType.WATER}:
                    tile.tile_type = TileType.ROAD

    def _build_demo_roads(self, grid: Grid) -> None:
        self._road_line(grid, 9, 9, 14, 9)
        self._road_line(grid, 14, 9, 14, 17)
        self._road_line(grid, 14, 17, 29, 17)
        self._road_line(grid, 29, 17, 29, 20)
        self._road_line(grid, 14, 17, 14, 24)
        self._road_line(grid, 14, 24, 11, 24)
        self._road_line(grid, 29, 17, 38, 17)
        self._road_line(grid, 38, 17, 38, 9)

    def _create_demo_stops(self, grid: Grid) -> list[Stop]:
        stop_specs = [
            (0, "North City Stop", 9, 9, "North City"),
            (1, "South City Stop", 29, 20, "South City"),
            (2, "Mine Stop", 38, 9, "Iron Mine"),
            (3, "Camp Stop", 11, 24, "Forest Camp"),
        ]
        stops: list[Stop] = []
        for stop_id, name, x, y, zone_name in stop_specs:
            tile = grid.get_tile(x, y)
            if tile is None:
                continue
            tile.has_stop = True
            tile.zone_name = zone_name
            stops.append(Stop(stop_id, name, x, y, zone_name))
        return stops
