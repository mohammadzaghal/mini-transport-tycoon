from __future__ import annotations

import random
from typing import Dict, List, Tuple

from src.enums import TileType
from src.models.grid import Grid
from src.models.facility import Facility
from src.config import FACILITY_NAME_TO_TYPE


CITY_SIZE  = 8
ROAD_COLS  = {2, 5}
ROAD_ROWS  = {2, 5}
BANK_CELLS = {(3, 3), (4, 3), (3, 4), (4, 4)}

_CITY_NAMES = ["Olympus Base", "Valles Station", "Arcadia Colony"]

_FACILITY_LAYOUTS: List[Tuple[str, int, int]] = [
    ("North Mine", 3, 3),
    ("South Mine", 3, 3),
    ("Fuel Rig", 2, 2),
    ("Aqua Dome N", 2, 2),
    ("Aqua Dome E", 2, 2),
    ("Aqua Dome S", 2, 2),
    ("Crystal Lab", 2, 2),
]

_LEGACY_CITIES: List[Tuple[str, int, int]] = [
    ("Olympus Base", 4, 3),
    ("Valles Station", 54, 3),
    ("Arcadia Colony", 28, 36),
]

_LEGACY_FACILITIES: List[Tuple[str, int, int, int, int, str]] = [
    ("North Mine", 30, 10, 3, 3, "south"),
    ("South Mine", 8, 44, 3, 3, "east"),
    ("Fuel Rig", 55, 35, 2, 2, "north"),
    ("Aqua Dome N", 0, 14, 2, 2, "east"),
    ("Aqua Dome E", 67, 14, 2, 2, "west"),
    ("Aqua Dome S", 34, 42, 2, 2, "north"),
    ("Crystal Lab", 14, 8, 2, 2, "south"),
]


class MapGenerator:
    def __init__(self, seed: int | None = None) -> None:
        if seed is None:
            seed = random.randrange(1 << 30)
        self.seed = seed
        self.rng = random.Random(seed)

    def generate(self, grid: Grid) -> Tuple[Dict[str, Facility], List[Tuple[str, int, int]]]:
        self._scatter_rocks(grid)
        self._place_ice_channels(grid)

        occupied: List[Tuple[int, int, int, int]] = []
        city_origins = self._place_cities_random(grid, occupied)

        self._place_city_hint_lakes(grid, city_origins)

        facilities: Dict[str, Facility] = {}
        self._place_facilities_random(grid, facilities, occupied)

        grid.facilities = facilities
        return facilities, city_origins

    @staticmethod
    def _bb_intersect(ax: int, ay: int, aw: int, ah: int, bx: int, by: int, bw: int, bh: int) -> bool:
        return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

    def _hits_occupied(
        self, occupied: List[Tuple[int, int, int, int]], sx: int, sy: int, w: int, h: int, margin: int
    ) -> bool:
        ax, ay = sx - margin, sy - margin
        aw, ah = w + 2 * margin, h + 2 * margin
        for bx, by, bw, bh in occupied:
            if self._bb_intersect(ax, ay, aw, ah, bx, by, bw, bh):
                return True
        return False

    def _footprint_is_grass_or_forest(self, grid: Grid, sx: int, sy: int, w: int, h: int) -> bool:
        for fy in range(sy, sy + h):
            for fx in range(sx, sx + w):
                t = grid.get_tile(fx, fy)
                if t is None or t.tile_type not in {TileType.GRASS, TileType.FOREST}:
                    return False
        return True

    def _place_cities_random(
        self, grid: Grid, occupied: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[str, int, int]]:
        out: List[Tuple[str, int, int]] = []
        margin = 4
        for name in _CITY_NAMES:
            placed = False
            for _ in range(900):
                sx = self.rng.randint(2, grid.width - CITY_SIZE - 2)
                sy = self.rng.randint(2, grid.height - CITY_SIZE - 2)
                if self._hits_occupied(occupied, sx, sy, CITY_SIZE, CITY_SIZE, margin):
                    continue
                if not self._footprint_is_grass_or_forest(grid, sx, sy, CITY_SIZE, CITY_SIZE):
                    continue
                self._place_city(grid, sx, sy, name)
                out.append((name, sx, sy))
                ox, oy = sx - margin, sy - margin
                occupied.append((ox, oy, CITY_SIZE + 2 * margin, CITY_SIZE + 2 * margin))
                placed = True
                break
            if not placed:
                for leg_name, lsx, lsy in _LEGACY_CITIES:
                    if leg_name != name:
                        continue
                    if self._hits_occupied(occupied, lsx, lsy, CITY_SIZE, CITY_SIZE, margin):
                        break
                    if not self._footprint_is_grass_or_forest(grid, lsx, lsy, CITY_SIZE, CITY_SIZE):
                        break
                    self._place_city(grid, lsx, lsy, name)
                    out.append((name, lsx, lsy))
                    ox, oy = lsx - margin, lsy - margin
                    occupied.append((ox, oy, CITY_SIZE + 2 * margin, CITY_SIZE + 2 * margin))
                    placed = True
                    break
            if not placed:
                for sy in range(2, grid.height - CITY_SIZE - 2):
                    for sx in range(2, grid.width - CITY_SIZE - 2):
                        if self._hits_occupied(occupied, sx, sy, CITY_SIZE, CITY_SIZE, margin):
                            continue
                        if not self._footprint_is_grass_or_forest(grid, sx, sy, CITY_SIZE, CITY_SIZE):
                            continue
                        self._place_city(grid, sx, sy, name)
                        out.append((name, sx, sy))
                        ox, oy = sx - margin, sy - margin
                        occupied.append((ox, oy, CITY_SIZE + 2 * margin, CITY_SIZE + 2 * margin))
                        placed = True
                        break
                    if placed:
                        break
            if not placed:
                raise RuntimeError("MapGenerator: could not place city {!r}".format(name))
        return out

    def _facility_entry_xy(self, sx: int, sy: int, w: int, h: int, entry_side: str) -> Tuple[int, int]:
        if entry_side == "west":
            return sx - 1, sy + h // 2
        if entry_side == "east":
            return sx + w, sy + h // 2
        if entry_side == "north":
            return sx + w // 2, sy - 1
        return sx + w // 2, sy + h

    def _entry_ok(self, grid: Grid, ex: int, ey: int) -> bool:
        t = grid.get_tile(ex, ey)
        return t is not None and t.tile_type in {TileType.GRASS, TileType.FOREST, TileType.WATER}

    def _try_place_facility(
        self,
        grid: Grid,
        facilities: Dict[str, Facility],
        occupied: List[Tuple[int, int, int, int]],
        name: str,
        w: int,
        h: int,
    ) -> bool:
        margin = 3
        sides = ["north", "south", "east", "west"]
        for _ in range(500):
            sx = self.rng.randint(2, grid.width - w - 2)
            sy = self.rng.randint(2, grid.height - h - 2)
            if self._hits_occupied(occupied, sx, sy, w, h, margin):
                continue
            if not self._footprint_is_grass_or_forest(grid, sx, sy, w, h):
                continue
            self.rng.shuffle(sides)
            for side in sides:
                ex, ey = self._facility_entry_xy(sx, sy, w, h, side)
                if not self._entry_ok(grid, ex, ey):
                    continue
                self._place_facility(grid, facilities, sx, sy, w, h, name, side)
                ox, oy = sx - margin, sy - margin
                occupied.append((ox, oy, w + 2 * margin, h + 2 * margin))
                return True
        return False

    def _place_facilities_random(
        self, grid: Grid, facilities: Dict[str, Facility], occupied: List[Tuple[int, int, int, int]]
    ) -> None:
        for name, w, h in _FACILITY_LAYOUTS:
            if self._try_place_facility(grid, facilities, occupied, name, w, h):
                continue
            placed = False
            for sx in range(2, grid.width - w - 2, 1):
                for sy in range(2, grid.height - h - 2, 1):
                    if self._hits_occupied(occupied, sx, sy, w, h, 3):
                        continue
                    if not self._footprint_is_grass_or_forest(grid, sx, sy, w, h):
                        continue
                    for side in ("south", "east", "north", "west"):
                        ex, ey = self._facility_entry_xy(sx, sy, w, h, side)
                        if self._entry_ok(grid, ex, ey):
                            self._place_facility(grid, facilities, sx, sy, w, h, name, side)
                            occupied.append((sx - 3, sy - 3, w + 6, h + 6))
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break
            if placed:
                continue
            for leg_name, lsx, lsy, lw, lh, lside in _LEGACY_FACILITIES:
                if leg_name != name:
                    continue
                self._place_facility(grid, facilities, lsx, lsy, lw, lh, name, lside)
                occupied.append((lsx - 3, lsy - 3, lw + 6, lh + 6))
                placed = True
                break
            if not placed:
                raise RuntimeError("MapGenerator: could not place facility {!r}".format(name))

    def _place_city_hint_lakes(self, grid: Grid, city_origins: List[Tuple[str, int, int]]) -> None:
        for _name, sx, sy in city_origins:
            for _ in range(24):
                lx = sx + self.rng.randint(-1, 7)
                ly = sy + self.rng.randint(6, 16)
                if lx < 1 or ly < 1 or lx >= grid.width - 1 or ly >= grid.height - 1:
                    continue
                self._place_lake(grid, lx, ly, radius=2)
                break

    def _scatter_rocks(self, grid: Grid) -> None:
        for tile in grid.iter_tiles():
            if self.rng.random() < 0.06:
                tile.tile_type = TileType.FOREST
                tile.tree_count = 1

        ccx = self.rng.randint(12, max(12, grid.width - 13))
        ccy = self.rng.randint(12, max(12, grid.height - 13))
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                tile = grid.get_tile(ccx + dx, ccy + dy)
                if tile is not None and tile.tile_type == TileType.GRASS and self.rng.random() < 0.55:
                    tile.tile_type = TileType.FOREST
                    tile.tree_count = 1

    def _place_ice_channels(self, grid: Grid) -> None:
        hy = self.rng.randint(6, max(6, grid.height - 7))
        self._carve_river(grid, start_x=0, start_y=hy, horizontal=True, length=grid.width)

        vx = self.rng.randint(8, max(8, grid.width - 9))
        vlen = self.rng.randint(18, max(18, min(50, grid.height - 6)))
        self._carve_river(grid, start_x=vx, start_y=0, horizontal=False, length=vlen)

        lr = self.rng.randint(3, 5)
        lx = self.rng.randint(lr + 8, max(lr + 8, grid.width - lr - 9))
        ly = self.rng.randint(lr + 8, max(lr + 8, grid.height - lr - 9))
        self._place_lake(grid, lx=lx, ly=ly, radius=lr)

        if self.rng.random() < 0.45:
            sr = 2
            sx = self.rng.randint(sr + 4, max(sr + 4, grid.width - sr - 5))
            sy = self.rng.randint(sr + 4, max(sr + 4, grid.height - sr - 5))
            self._place_lake(grid, lx=sx, ly=sy, radius=sr)

    def _carve_river(
        self, grid: Grid, start_x: int, start_y: int, horizontal: bool, length: int
    ) -> None:
        x, y = start_x, start_y
        for _ in range(length):
            for width in range(-1, 2):
                if horizontal:
                    tx, ty = x, y + width
                else:
                    tx, ty = x + width, y
                tile = grid.get_tile(tx, ty)
                if tile is not None and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                    tile.tile_type = TileType.WATER
                    tile.tree_count = 0

            if horizontal:
                x += 1
                if self.rng.random() < 0.2:
                    y += self.rng.choice([-1, 1])
                y = max(2, min(grid.height - 3, y))
            else:
                y += 1
                if self.rng.random() < 0.2:
                    x += self.rng.choice([-1, 1])
                x = max(2, min(grid.width - 3, x))

    def _place_lake(self, grid: Grid, lx: int, ly: int, radius: int) -> None:
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    tile = grid.get_tile(lx + dx, ly + dy)
                    if tile is not None and tile.tile_type in {TileType.GRASS, TileType.FOREST}:
                        tile.tile_type = TileType.WATER
                        tile.tree_count = 0

    def _place_city(self, grid: Grid, sx: int, sy: int, city_name: str) -> None:
        for rel_y in range(CITY_SIZE):
            for rel_x in range(CITY_SIZE):
                ax, ay = sx + rel_x, sy + rel_y
                tile = grid.get_tile(ax, ay)
                if tile is None:
                    continue
                tile.zone_name = city_name
                tile.tree_count = 0
                tile.tile_type = TileType.WATER if tile.tile_type == TileType.WATER else TileType.CITY

                is_road = (rel_x in ROAD_COLS) or (rel_y in ROAD_ROWS)
                is_bank = (rel_x, rel_y) in BANK_CELLS

                if is_road:
                    tile.tile_type = TileType.ROAD
                    tile.is_city_road = True
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
        facilities: Dict[str, Facility],
        sx: int, sy: int,
        w: int, h: int,
        name: str,
        entry_side: str,
    ) -> None:
        fac_type = FACILITY_NAME_TO_TYPE.get(name)
        facility = Facility(name=name, fac_type=fac_type, x=sx, y=sy) if fac_type else None

        for fy in range(sy, sy + h):
            for fx in range(sx, sx + w):
                tile = grid.get_tile(fx, fy)
                if tile is None:
                    continue
                tile.tile_type = TileType.FACILITY
                tile.zone_name = name
                tile.tree_count = 0
                if facility is not None:
                    tile.facility_ref = facility

        if entry_side == "west":
            ex, ey = sx - 1, sy + h // 2
        elif entry_side == "east":
            ex, ey = sx + w, sy + h // 2
        elif entry_side == "north":
            ex, ey = sx + w // 2, sy - 1
        else:
            ex, ey = sx + w // 2, sy + h

        entry = grid.get_tile(ex, ey)
        if entry is not None and entry.tile_type in {TileType.GRASS, TileType.FOREST, TileType.WATER}:
            entry.tile_type = TileType.ROAD
            entry.zone_name = name
            entry.is_entry_point = True
            entry.tree_count = 0
            if facility is not None:
                entry.facility_ref = facility

        if facility is not None:
            facilities[name] = facility

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