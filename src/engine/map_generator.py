from __future__ import annotations

import random
from typing import List

from src.enums import TileType
from src.models.grid import Grid


# City layout constants
CITY_SIZE = 8
ROAD_COLS = {2, 5}
ROAD_ROWS = {2, 5}
BANK_CELLS = {(3, 3), (4, 3), (3, 4), (4, 4)}


class MapGenerator:
    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def generate(self, grid: Grid) -> List:
        self._scatter_forests(grid)

        self._place_city(grid, 3,  2,  "Greenfield")
        self._place_city(grid, 36, 2,  "Riverside")
        self._place_city(grid, 20, 28, "Southport")

        self._place_facility(grid, 48, 4,  3, 3, "Iron Mine",    entry_side="west")
        self._place_facility(grid, 50, 25, 2, 2, "Coal Depot",   entry_side="west")
        self._place_facility(grid, 3,  36, 3, 3, "Lumber Yard",  entry_side="east")
        self._place_facility(grid, 28, 15, 3, 3, "Steel Mill",   entry_side="west")
        self._place_facility(grid, 15, 14, 2, 2, "Farm",         entry_side="north")

        return []

    def _scatter_forests(self, grid: Grid) -> None:
        for tile in grid.iter_tiles():
            if self.rng.random() < 0.06:
                tile.tile_type = TileType.FOREST
                tile.tree_count = 1

    def _place_city(self, grid: Grid, sx: int, sy: int, city_name: str) -> None:
        for rel_y in range(CITY_SIZE):
            for rel_x in range(CITY_SIZE):
                ax, ay = sx + rel_x, sy + rel_y
                tile = grid.get_tile(ax, ay)
                if tile is None:
                    continue

                tile.zone_name = city_name
                tile.tree_count = 0

                is_road = (rel_x in ROAD_COLS) or (rel_y in ROAD_ROWS)
                is_bank = (rel_x, rel_y) in BANK_CELLS

                if is_road:
                    tile.tile_type = TileType.ROAD
                elif is_bank:
                    tile.tile_type = TileType.CITY
                    tile.is_bank = True
                else:
                    tile.tile_type = TileType.CITY

        entry = grid.get_tile(sx + 2, sy + 3)
        if entry is not None:
            entry.is_entry_point = True

    def _place_facility(
        self,
        grid: Grid,
        sx: int,
        sy: int,
        w: int,
        h: int,
        name: str,
        entry_side: str,
    ) -> None:
        for fy in range(sy, sy + h):
            for fx in range(sx, sx + w):
                tile = grid.get_tile(fx, fy)
                if tile is None:
                    continue
                tile.tile_type = TileType.FACILITY
                tile.zone_name = name
                tile.tree_count = 0

        if entry_side == "west":
            ex, ey = sx - 1, sy + h // 2
        elif entry_side == "east":
            ex, ey = sx + w, sy + h // 2
        elif entry_side == "north":
            ex, ey = sx + w // 2, sy - 1
        else:
            ex, ey = sx + w // 2, sy + h

        entry = grid.get_tile(ex, ey)
        if entry is not None and entry.tile_type == TileType.GRASS:
            entry.tile_type = TileType.ROAD
            entry.zone_name = name
            entry.is_entry_point = True
        elif entry is not None and entry.tile_type == TileType.FOREST:
            entry.tile_type = TileType.ROAD
            entry.zone_name = name
            entry.is_entry_point = True
            entry.tree_count = 0

    def _road_line(self, grid: Grid, x1: int, y1: int, x2: int, y2: int) -> None:
        if x1 == x2:
            y_start, y_end = sorted((y1, y2))
            for y in range(y_start, y_end + 1):
                tile = grid.get_tile(x1, y)
                if tile and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                    tile.tile_type = TileType.ROAD
                    tile.tree_count = 0
        elif y1 == y2:
            x_start, x_end = sorted((x1, x2))
            for x in range(x_start, x_end + 1):
                tile = grid.get_tile(x, y1)
                if tile and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                    tile.tile_type = TileType.ROAD
                    tile.tree_count = 0

    def _build_road_network(self, grid: Grid) -> None:
        self._road_line(grid, 5,  10, 5,  14)
        self._road_line(grid, 5,  14, 47, 14)
        self._road_line(grid, 47, 14, 47, 6)
        self._road_line(grid, 47,  6, 48,  6)

        self._road_line(grid, 11,  4, 36,  4)

        self._road_line(grid, 38, 10, 38, 14)
        self._road_line(grid, 41, 10, 41, 14)

        self._road_line(grid, 22, 28, 22, 14)

        self._road_line(grid, 27, 30, 47, 30)
        self._road_line(grid, 47, 30, 47, 27)
        self._road_line(grid, 47, 27, 50, 27)
        self._road_line(grid, 50, 27, 50, 26)

        self._road_line(grid, 6,  37, 6,  30)
        self._road_line(grid, 6,  30, 20, 30)

        self._road_line(grid, 27, 16, 27, 14)

        self._road_line(grid, 15, 13, 15, 14)
        self._road_line(grid, 15, 14, 16, 14)