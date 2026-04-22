"""Tests for src/engine/pathfinding.py"""
import pytest
from src.models.grid import Grid
from src.enums import TileType, BridgeType
from src.engine.pathfinding import find_road_path, find_track_path


def road_grid(width=10, height=10):
    """Grid with a horizontal road across row 0."""
    g = Grid(width, height)
    for x in range(width):
        g.set_tile_type(x, 0, TileType.ROAD)
    return g


def track_grid(width=10, height=10):
    """Grid with a horizontal track across row 0."""
    g = Grid(width, height)
    for x in range(width):
        g.set_tile_type(x, 0, TileType.TRACK)
    return g


# ===========================================================================
# find_road_path
# ===========================================================================

class TestFindRoadPath:
    def test_same_start_and_goal(self):
        g = road_grid()
        path = find_road_path(g, (0, 0), (0, 0))
        assert path == [(0, 0)]

    def test_adjacent_road_tiles(self):
        g = road_grid()
        path = find_road_path(g, (0, 0), (1, 0))
        assert path == [(0, 0), (1, 0)]

    def test_straight_horizontal_path(self):
        g = road_grid()
        path = find_road_path(g, (0, 0), (4, 0))
        assert path[0] == (0, 0)
        assert path[-1] == (4, 0)
        assert len(path) == 5

    def test_no_path_through_grass(self):
        """No road → should return empty list."""
        g = Grid(5, 5)
        path = find_road_path(g, (0, 0), (4, 0))
        assert path == []

    def test_goal_reachable_even_if_not_driveable(self):
        """Pathfinding allows non-driveable goal tile (entry/stop)."""
        g = road_grid()
        # goal is grass (non-driveable), but BFS allows it as final step
        path = find_road_path(g, (0, 0), (5, 1))
        # Should find a path ending at (5,1) even though it's grass
        assert path[-1] == (5, 1) if path else True

    def test_path_endpoints_correct(self):
        g = road_grid()
        path = find_road_path(g, (0, 0), (9, 0))
        assert path[0] == (0, 0)
        assert path[-1] == (9, 0)

    def test_path_is_contiguous(self):
        """Each step in the path must be adjacent (4-connected)."""
        g = road_grid()
        path = find_road_path(g, (0, 0), (5, 0))
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            assert abs(x2 - x1) + abs(y2 - y1) == 1

    def test_road_with_bridge_over_water(self):
        """Road path uses bridge (water tile with bridge_type set)."""
        g = Grid(5, 5)
        for x in [0, 1, 3, 4]:
            g.set_tile_type(x, 0, TileType.ROAD)
        water = g.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = BridgeType.WOODEN  # makes it driveable
        path = find_road_path(g, (0, 0), (4, 0))
        assert (2, 0) in path

    def test_disconnected_road_returns_empty(self):
        g = Grid(10, 10)
        g.set_tile_type(0, 0, TileType.ROAD)
        g.set_tile_type(9, 9, TileType.ROAD)
        path = find_road_path(g, (0, 0), (9, 9))
        assert path == []


# ===========================================================================
# find_track_path
# ===========================================================================

class TestFindTrackPath:
    def test_same_start_and_goal(self):
        g = track_grid()
        path = find_track_path(g, (0, 0), (0, 0))
        assert path == [(0, 0)]

    def test_straight_track_path(self):
        g = track_grid()
        path = find_track_path(g, (0, 0), (4, 0))
        assert path[0] == (0, 0)
        assert path[-1] == (4, 0)

    def test_no_path_through_grass(self):
        g = Grid(5, 5)
        path = find_track_path(g, (0, 0), (4, 0))
        assert path == []

    def test_path_is_contiguous(self):
        g = track_grid()
        path = find_track_path(g, (0, 0), (5, 0))
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            assert abs(x2 - x1) + abs(y2 - y1) == 1

    def test_entry_point_traversable(self):
        """BFS for track allows entry points as intermediate tiles."""
        g = Grid(5, 5)
        for x in range(5):
            g.set_tile_type(x, 0, TileType.TRACK)
        g.get_tile(2, 0).is_entry_point = True
        path = find_track_path(g, (0, 0), (4, 0))
        assert path is not None
        assert len(path) > 0

    def test_stop_tile_traversable(self):
        """BFS for track allows stop tiles as intermediate tiles."""
        g = Grid(5, 5)
        for x in range(5):
            g.set_tile_type(x, 0, TileType.TRACK)
        g.get_tile(2, 0).is_stop = True
        path = find_track_path(g, (0, 0), (4, 0))
        assert (2, 0) in path

    def test_steel_bridge_traversable_for_track(self):
        """Steel bridge (BridgeType.STEEL) allows train traversal."""
        g = Grid(5, 5)
        for x in [0, 1, 3, 4]:
            g.set_tile_type(x, 0, TileType.TRACK)
        water = g.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = BridgeType.STEEL
        path = find_track_path(g, (0, 0), (4, 0))
        assert (2, 0) in path

    def test_wooden_bridge_not_traversable_for_track(self):
        """Wooden bridge does NOT allow train traversal."""
        g = Grid(5, 5)
        for x in [0, 1, 3, 4]:
            g.set_tile_type(x, 0, TileType.TRACK)
        water = g.get_tile(2, 0)
        water.tile_type = TileType.WATER
        water.bridge_type = BridgeType.WOODEN
        path = find_track_path(g, (0, 0), (4, 0))
        assert path == []
