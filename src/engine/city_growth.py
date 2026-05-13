from __future__ import annotations

from typing import Dict, Set, Tuple

from src.enums import TileType
from src.config import CITY_GROWTH_POINTS_PER_DELIVERY, CITY_GROWTH_THRESHOLD


class CityGrowthManager:
    """Manages city expansion triggered by cargo and passenger deliveries.

    Each registered city accumulates growth points when vehicles deliver
    goods to it.  When a city's points reach ``CITY_GROWTH_THRESHOLD`` the
    city expands by converting adjacent grass or forest tiles into city
    blocks and road tiles, following a regular grid pattern relative to
    the city's origin tile.
    """

    def __init__(self) -> None:
        """Initialise an empty growth manager with no registered cities."""
        self._points: Dict[str, float] = {}
        self._city_origins: Dict[str, Tuple[int, int]] = {}

    def register_city(self, city_name: str, sx: int, sy: int) -> None:
        """Register a city so it can receive growth points.

        If the city is already registered its origin is updated but its
        accumulated points are preserved.

        Args:
            city_name: Unique name identifier for the city.
            sx: Tile column of the city's origin (anchor) tile.
            sy: Tile row of the city's origin (anchor) tile.
        """
        self._points.setdefault(city_name, 0.0)
        self._city_origins[city_name] = (sx, sy)

    def on_delivery(self, city_name: str) -> None:
        """Award growth points to a city for a completed delivery.

        Does nothing if the city has not been registered.

        Args:
            city_name: The name of the city that received the delivery.
        """
        if city_name in self._points:
            self._points[city_name] += CITY_GROWTH_POINTS_PER_DELIVERY

    def tick(self, grid, renderer, minimap=None) -> None:
        """Check all cities and trigger expansion for those above the threshold.

        For each city whose accumulated points meet or exceed
        ``CITY_GROWTH_THRESHOLD``, points are reduced by the threshold amount
        and the city is expanded by one ring of tiles.

        Args:
            grid: The game Grid used to locate and modify tiles.
            renderer: The MapRenderer used to update the visual tile cache.
            minimap: Optional Minimap instance to keep in sync; may be None.
        """
        for city_name, points in list(self._points.items()):
            if points >= CITY_GROWTH_THRESHOLD:
                self._points[city_name] -= CITY_GROWTH_THRESHOLD
                self._expand_city(city_name, grid, renderer, minimap)

    def _expand_city(self, city_name: str, grid, renderer, minimap=None) -> None:
        """Expand a single city by converting its neighbouring unclaimed tiles.

        Tiles adjacent to the city's current footprint that are unoccupied
        grass or forest are converted to city blocks or road tiles.  Roads
        are placed on a regular 3-tile grid pattern relative to the city
        origin to produce a street layout.

        Args:
            city_name: Name of the city to expand.
            grid: The game Grid to modify.
            renderer: MapRenderer for updating the rendered tile cache.
            minimap: Optional Minimap to keep synchronised; may be None.
        """
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
        """Return the current growth-point balance for a city.

        Args:
            city_name: The city to query.

        Returns:
            Accumulated growth points, or 0.0 if the city is not registered.
        """
        return self._points.get(city_name, 0.0)