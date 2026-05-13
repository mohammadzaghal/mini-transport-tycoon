from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from src.enums import TileType
from src.models.tile import Tile

class Grid:
    """The game map represented as a 2-D array of Tile objects.

    Attributes:
        width: Number of tiles in the horizontal direction.
        height: Number of tiles in the vertical direction.
        facilities: Mapping of (x, y) tuples to Facility objects placed on the map.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialise a grid filled with default GRASS tiles.

        Args:
            width: Number of columns.
            height: Number of rows.
        """
        self.width = width
        self.height = height
        self._tiles = [
            [Tile(x=x, y=y) for x in range(width)]
            for y in range(height)
        ]
        self.facilities: dict = {}

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if the coordinates fall within the grid boundaries.

        Args:
            x: Tile column index.
            y: Tile row index.

        Returns:
            True when (x, y) is a valid grid position, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Retrieve the Tile at the given coordinates.

        Args:
            x: Tile column index.
            y: Tile row index.

        Returns:
            The Tile at (x, y), or None if the position is out of bounds.
        """
        if not self.in_bounds(x, y):
            return None
        return self._tiles[y][x]

    def set_tile_type(self, x: int, y: int, tile_type: TileType) -> None:
        """Change the TileType of the tile at the given position.

        Does nothing if the coordinates are out of bounds.

        Args:
            x: Tile column index.
            y: Tile row index.
            tile_type: The new TileType to assign.
        """
        tile = self.get_tile(x, y)
        if tile is not None:
            tile.tile_type = tile_type

    def neighbors4(self, x: int, y: int) -> list:
        """Return the up-to-four orthogonal neighbours of a tile.

        Neighbours that fall outside the grid boundary are excluded.

        Args:
            x: Tile column index.
            y: Tile row index.

        Returns:
            A list of Tile objects adjacent to (x, y) in the four cardinal
            directions (east, west, south, north).
        """
        neighbors = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tile = self.get_tile(x + dx, y + dy)
            if tile is not None:
                neighbors.append(tile)
        return neighbors

    def iter_tiles(self) -> Iterable:
        """Yield every Tile in the grid in row-major order (top-left to bottom-right).

        Returns:
            An iterable of all Tile objects in the grid.
        """
        for row in self._tiles:
            yield from row

    def is_road_buildable(self, x: int, y: int) -> bool:
        """Check whether a player-built road can be placed at the given position.

        Roads may only be placed on GRASS or FOREST tiles that are not already
        part of a city road network.

        Args:
            x: Tile column index.
            y: Tile row index.

        Returns:
            True if a road can be built here, False otherwise.
        """
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        if tile.is_city_road:
            return False
        return tile.tile_type in {TileType.GRASS, TileType.FOREST}

    def is_track_buildable(self, x: int, y: int) -> bool:
        """Check whether a rail track can be placed at the given position.

        Tracks may be placed on GRASS, FOREST, existing TRACK, or ROAD tiles,
        but not on facility entry-point tiles.

        Args:
            x: Tile column index.
            y: Tile row index.

        Returns:
            True if a track can be built here, False otherwise.
        """
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        if tile.is_entry_point:
            return False
        return tile.tile_type in {TileType.GRASS, TileType.FOREST, TileType.TRACK, TileType.ROAD}