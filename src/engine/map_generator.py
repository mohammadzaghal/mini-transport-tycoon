from __future__ import annotations

import random
from typing import List

from src.enums import TileType
from src.models.grid import Grid

CITY_SIZE = 8
ROAD_COLS = {2, 5}
ROAD_ROWS = {2, 5}
BANK_CELLS = {(3, 3), (4, 3), (3, 4), (4, 4)}


class MapGenerator:
    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def generate(self, grid: Grid) -> List:
        self._scatter_forests(grid)

        self._place_city(grid, 3, 2, "Greenfield")
        self._place_city(grid, 36, 2, "Riverside")
        self._place_city(grid, 20, 28, "Southport")

        self._place_facility(grid, 48, 4, 3, 3, "Iron Mine", entry_side="west")
        self._place_facility(grid, 50, 25, 2, 2, "Coal Depot", entry_side="west")
        self._place_facility(grid, 3, 36, 3, 3, "Lumber Yard", entry_side="east")
        self._place_facility(grid, 28, 15, 3, 3, "Steel Mill", entry_side="west")
        self._place_facility(grid, 15, 14, 2, 2, "Farm", entry_side="north")

        return []

    def _scatter_forests(self, grid: Grid) -> None:
        for tile in grid.iter_tiles():
            if self.rng.random() < 0.06:
                tile.tile_type = TileType.FOREST
                tile.tree_count = 1

    def _place_city(self, grid: Grid, sx: int, sy: int, city_name: str) -> None:
        for rel_y in range(CITY_SIZE):
            for rel_x in range(CITY_SIZE):
                tile = grid.get_tile(sx + rel_x, sy + rel_y)
                if tile is None:
                    continue

                tile.zone_name = city_name
                tile.tree_count = 0

                if rel_x in ROAD_COLS or rel_y in ROAD_ROWS:
                    tile.tile_type = TileType.ROAD
                elif (rel_x, rel_y) in BANK_CELLS:
                    tile.tile_type = TileType.CITY
                    tile.is_bank = True
                else:
                    tile.tile_type = TileType.CITY

        entry = grid.get_tile(sx + 2, sy + 3)
        if entry:
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
        for y in range(sy, sy + h):
            for x in range(sx, sx + w):
                tile = grid.get_tile(x, y)
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
        if entry and entry.tile_type in {TileType.GRASS, TileType.FOREST}:
            entry.tile_type = TileType.ROAD
            entry.zone_name = name
            entry.is_entry_point = True
            entry.tree_count = 0

    def _road_line(self, grid: Grid, x1: int, y1: int, x2: int, y2: int) -> None:
        if x1 == x2:
            for y in range(*sorted((y1, y2)), +1):
                tile = grid.get_tile(x1, y)
                if tile and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                    tile.tile_type = TileType.ROAD
                    tile.tree_count = 0
        elif y1 == y2:
            for x in range(*sorted((x1, x2)), +1):
                tile = grid.get_tile(x, y1)
                if tile and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                    tile.tile_type = TileType.ROAD
                    tile.tree_count = 0