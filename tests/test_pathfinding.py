"""Unit tests for src.engine.pathfinding.

These tests build small synthetic grids so they are fast and deterministic,
and they never touch pygame (pathfinding only depends on Grid/Tile/enums).
"""
from __future__ import annotations

import pytest

from src.engine.pathfinding import find_road_path, find_track_path
from src.enums import BridgeType, TileType
from src.models.grid import Grid


def _blank_grid(w: int = 5, h: int = 5) -> Grid:
    """Return a grid of all-GRASS tiles (nothing driveable)."""
    return Grid(w, h)


def _paint_road(grid: Grid, cells) -> None:
    for (x, y) in cells:
        grid.set_tile_type(x, y, TileType.ROAD)


def _paint_track(grid: Grid, cells) -> None:
    for (x, y) in cells:
        grid.set_tile_type(x, y, TileType.TRACK)


class TestFindRoadPath:
    def test_start_equals_goal_returns_single_tile(self):
        grid = _blank_grid()
        assert find_road_path(grid, (2, 2), (2, 2)) == [(2, 2)]

    def test_straight_horizontal_road(self):
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0), (2, 0), (3, 0)])
        path = find_road_path(grid, (0, 0), (3, 0))
        assert path == [(0, 0), (1, 0), (2, 0), (3, 0)]

    def test_l_shaped_road(self):
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)])
        path = find_road_path(grid, (0, 0), (2, 2))
        assert path[0] == (0, 0)
        assert path[-1] == (2, 2)
        # BFS gives the shortest path; with this layout only one path exists
        assert path == [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]

    def test_no_road_returns_empty(self):
        grid = _blank_grid()
        assert find_road_path(grid, (0, 0), (3, 3)) == []

    def test_disconnected_roads_return_empty(self):
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0)])          # island A
        _paint_road(grid, [(3, 3), (4, 3)])          # island B, not connected
        assert find_road_path(grid, (0, 0), (4, 3)) == []

    def test_grass_gap_is_not_traversable(self):
        """A single grass tile between two road tiles must break the path."""
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0), (3, 0), (4, 0)])  # gap at (2,0)
        assert find_road_path(grid, (0, 0), (4, 0)) == []

    def test_bridge_allows_crossing_water(self):
        grid = _blank_grid(6, 1)
        _paint_road(grid, [(0, 0), (1, 0), (3, 0), (4, 0), (5, 0)])
        # Water tile with a wooden bridge should be driveable for road vehicles
        water = grid.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = BridgeType.WOODEN
        path = find_road_path(grid, (0, 0), (5, 0))
        assert path == [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]

    def test_water_without_bridge_blocks(self):
        grid = _blank_grid(6, 1)
        _paint_road(grid, [(0, 0), (1, 0), (3, 0), (4, 0), (5, 0)])
        grid.get_tile(2, 0).tile_type = TileType.WATER  # no bridge_type
        assert find_road_path(grid, (0, 0), (5, 0)) == []

    def test_goal_tile_is_accepted_even_if_not_driveable(self):
        """The BFS explicitly allows the goal tile itself to be non-driveable
        (e.g. a city/facility entry point sitting on a non-ROAD tile)."""
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0), (2, 0)])
        # (3, 0) is still GRASS (not driveable) but is the goal
        path = find_road_path(grid, (0, 0), (3, 0))
        assert path == [(0, 0), (1, 0), (2, 0), (3, 0)]

    def test_bfs_returns_shortest_when_multiple_routes_exist(self):
        """Fill a rectangle with road; BFS should pick a length-5 path from
        (0,0) to (2,2), not a meandering one."""
        grid = _blank_grid(3, 3)
        for y in range(3):
            for x in range(3):
                grid.set_tile_type(x, y, TileType.ROAD)
        path = find_road_path(grid, (0, 0), (2, 2))
        assert len(path) == 5
        assert path[0] == (0, 0)
        assert path[-1] == (2, 2)


class TestFindTrackPath:
    def test_start_equals_goal_returns_single_tile(self):
        grid = _blank_grid()
        assert find_track_path(grid, (1, 1), (1, 1)) == [(1, 1)]

    def test_straight_track(self):
        grid = _blank_grid()
        _paint_track(grid, [(0, 0), (1, 0), (2, 0)])
        assert find_track_path(grid, (0, 0), (2, 0)) == [(0, 0), (1, 0), (2, 0)]

    def test_road_does_not_count_as_track(self):
        """Roads are not track-traversable, so a pure-road corridor must fail."""
        grid = _blank_grid()
        _paint_road(grid, [(0, 0), (1, 0), (2, 0)])
        assert find_track_path(grid, (0, 0), (2, 0)) == []

    def test_steel_bridge_allows_train_crossing(self):
        grid = _blank_grid(5, 1)
        _paint_track(grid, [(0, 0), (1, 0), (3, 0), (4, 0)])
        water = grid.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = BridgeType.STEEL
        path = find_track_path(grid, (0, 0), (4, 0))
        assert path == [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]

    @pytest.mark.parametrize("bridge", [BridgeType.WOODEN, BridgeType.STONE])
    def test_non_steel_bridge_blocks_trains(self, bridge):
        grid = _blank_grid(5, 1)
        _paint_track(grid, [(0, 0), (1, 0), (3, 0), (4, 0)])
        water = grid.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = bridge
        assert find_track_path(grid, (0, 0), (4, 0)) == []

    def test_entry_point_is_traversable_even_without_track(self):
        """Per the docstring: entry points and stops may sit on ROAD tiles but
        should still be treated as traversable so trains can reach them."""
        grid = _blank_grid()
        _paint_track(grid, [(0, 0), (1, 0), (2, 0)])
        # (3, 0) is a ROAD tile flagged as an entry point
        entry = grid.get_tile(3, 0)
        entry.tile_type = TileType.ROAD
        entry.is_entry_point = True
        path = find_track_path(grid, (0, 0), (3, 0))
        assert path == [(0, 0), (1, 0), (2, 0), (3, 0)]

    def test_stop_tile_is_traversable_even_without_track(self):
        grid = _blank_grid()
        _paint_track(grid, [(0, 0), (1, 0)])
        stop = grid.get_tile(2, 0)
        stop.tile_type = TileType.ROAD
        stop.is_stop = True
        path = find_track_path(grid, (0, 0), (2, 0))
        assert path == [(0, 0), (1, 0), (2, 0)]

    def test_no_connection_returns_empty(self):
        grid = _blank_grid()
        _paint_track(grid, [(0, 0), (1, 0)])
        _paint_track(grid, [(4, 4)])
        assert find_track_path(grid, (0, 0), (4, 4)) == []
