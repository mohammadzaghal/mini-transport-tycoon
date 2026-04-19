from __future__ import annotations

from typing import Dict, Set, Tuple

from src.enums import TileType
from src.config import CITY_GROWTH_POINTS_PER_DELIVERY, CITY_GROWTH_THRESHOLD


class CityGrowthManager:
    def __init__(self) -> None:
        self._points: Dict[str, float] = {}
        self._city_origins: Dict[str, Tuple[int, int]] = {}

    def register_city(self, city_name: str, sx: int, sy: int) -> None:
        self._points.setdefault(city_name, 0.0)
        self._city_origins[city_name] = (sx, sy)

    def on_delivery(self, city_name: str) -> None:
        if city_name in self._points:
            self._points[city_name] += CITY_GROWTH_POINTS_PER_DELIVERY

    def tick(self, grid, renderer, minimap=None) -> None:
        for city_name, points in list(self._points.items()):
            if points >= CITY_GROWTH_THRESHOLD:
                self._points[city_name] -= CITY_GROWTH_THRESHOLD
                self._expand_city(city_name, grid, renderer, minimap)

    def _expand_city(self, city_name: str, grid, renderer, minimap=None) -> None:
        origin = self._city_origins.get(city_name)
        if origin is None:
            return
        ox, oy = origin

        expansion_set: Set[Tuple[int, int]] = set()
        for tile in grid.iter_tiles():
            belongs = (
                tile.zone_name == city_name
                and tile.tile_type in {TileType.CITY, TileType.ROAD}
            )
            if not belongs:
                continue
            for nb in grid.neighbors4(tile.x, tile.y):
                if nb.zone_name == "" and nb.tile_type in {TileType.GRASS, TileType.FOREST}:
                    expansion_set.add((nb.x, nb.y))

        if not expansion_set:
            return

        for ex, ey in expansion_set:
            new_tile = grid.get_tile(ex, ey)
            if new_tile is None:
                continue

            rel_x = ex - ox
            rel_y = ey - oy
            on_road = (rel_x % 3 == 2) or (rel_y % 3 == 2)

            new_tile.zone_name = city_name
            new_tile.tree_count = 0
            if on_road:
                new_tile.tile_type = TileType.ROAD
                new_tile.is_city_road = True
            else:
                new_tile.tile_type = TileType.CITY

            if renderer is not None:
                renderer.update_tile(ex, ey, new_tile)
            if minimap is not None:
                minimap.update_tile(ex, ey, new_tile)

    def points(self, city_name: str) -> float:
        return self._points.get(city_name, 0.0)