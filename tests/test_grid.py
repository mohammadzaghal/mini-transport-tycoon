"""Tests for src/models/grid.py"""
import pytest
from src.models.grid import Grid
from src.enums import TileType


def make_grid(w=10, h=10):
    return Grid(w, h)


class TestGridInit:
    def test_dimensions_stored(self):
        g = make_grid(5, 8)
        assert g.width == 5
        assert g.height == 8

    def test_all_tiles_start_as_grass(self):
        g = make_grid(4, 4)
        for tile in g.iter_tiles():
            assert tile.tile_type == TileType.GRASS

    def test_tile_positions_correct(self):
        g = make_grid(3, 3)
        for y in range(3):
            for x in range(3):
                t = g.get_tile(x, y)
                assert t.x == x
                assert t.y == y


class TestGridInBounds:
    def test_origin_in_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(0, 0) is True

    def test_last_tile_in_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(4, 4) is True

    def test_negative_x_out_of_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(-1, 0) is False

    def test_negative_y_out_of_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(0, -1) is False

    def test_x_equal_width_out_of_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(5, 0) is False

    def test_y_equal_height_out_of_bounds(self):
        g = make_grid(5, 5)
        assert g.in_bounds(0, 5) is False


class TestGridGetTile:
    def test_returns_correct_tile(self):
        g = make_grid(5, 5)
        t = g.get_tile(2, 3)
        assert t.x == 2
        assert t.y == 3

    def test_out_of_bounds_returns_none(self):
        g = make_grid(5, 5)
        assert g.get_tile(-1, 0) is None
        assert g.get_tile(10, 10) is None

    def test_edge_tile_accessible(self):
        g = make_grid(10, 10)
        assert g.get_tile(9, 9) is not None


class TestGridSetTileType:
    def test_sets_tile_type(self):
        g = make_grid()
        g.set_tile_type(3, 3, TileType.ROAD)
        assert g.get_tile(3, 3).tile_type == TileType.ROAD

    def test_out_of_bounds_does_not_crash(self):
        g = make_grid()
        g.set_tile_type(999, 999, TileType.WATER)  # must not raise


class TestGridNeighbors4:
    def test_center_tile_has_four_neighbors(self):
        g = make_grid(5, 5)
        nbs = g.neighbors4(2, 2)
        assert len(nbs) == 4

    def test_corner_tile_has_two_neighbors(self):
        g = make_grid(5, 5)
        nbs = g.neighbors4(0, 0)
        assert len(nbs) == 2

    def test_edge_tile_has_three_neighbors(self):
        g = make_grid(5, 5)
        nbs = g.neighbors4(0, 2)
        assert len(nbs) == 3

    def test_neighbor_positions_are_adjacent(self):
        g = make_grid(5, 5)
        nbs = g.neighbors4(2, 2)
        positions = {(n.x, n.y) for n in nbs}
        assert (1, 2) in positions
        assert (3, 2) in positions
        assert (2, 1) in positions
        assert (2, 3) in positions


class TestGridIterTiles:
    def test_iter_yields_all_tiles(self):
        g = make_grid(3, 4)
        tiles = list(g.iter_tiles())
        assert len(tiles) == 12

    def test_iter_tiles_all_unique_positions(self):
        g = make_grid(4, 4)
        positions = [(t.x, t.y) for t in g.iter_tiles()]
        assert len(positions) == len(set(positions))


class TestGridIsRoadBuildable:
    def test_grass_is_road_buildable(self):
        g = make_grid()
        assert g.is_road_buildable(5, 5) is True

    def test_forest_is_road_buildable(self):
        g = make_grid()
        g.set_tile_type(3, 3, TileType.FOREST)
        assert g.is_road_buildable(3, 3) is True

    def test_road_tile_not_road_buildable(self):
        """Can't build a road on an existing road."""
        g = make_grid()
        g.set_tile_type(3, 3, TileType.ROAD)
        assert g.is_road_buildable(3, 3) is False

    def test_water_not_road_buildable(self):
        g = make_grid()
        g.set_tile_type(3, 3, TileType.WATER)
        assert g.is_road_buildable(3, 3) is False

    def test_city_road_not_road_buildable(self):
        g = make_grid()
        t = g.get_tile(3, 3)
        t.is_city_road = True
        assert g.is_road_buildable(3, 3) is False

    def test_out_of_bounds_not_road_buildable(self):
        g = make_grid()
        assert g.is_road_buildable(999, 999) is False


class TestGridIsTrackBuildable:
    def test_grass_is_track_buildable(self):
        g = make_grid()
        assert g.is_track_buildable(5, 5) is True

    def test_road_is_track_buildable(self):
        g = make_grid()
        g.set_tile_type(3, 3, TileType.ROAD)
        assert g.is_track_buildable(3, 3) is True

    def test_water_not_track_buildable(self):
        g = make_grid()
        g.set_tile_type(3, 3, TileType.WATER)
        assert g.is_track_buildable(3, 3) is False

    def test_entry_point_not_track_buildable(self):
        g = make_grid()
        g.get_tile(3, 3).is_entry_point = True
        assert g.is_track_buildable(3, 3) is False

    def test_out_of_bounds_not_track_buildable(self):
        g = make_grid()
        assert g.is_track_buildable(-1, -1) is False
