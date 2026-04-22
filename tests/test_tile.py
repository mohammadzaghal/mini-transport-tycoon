"""Tests for src/models/tile.py"""
import pytest
from src.models.tile import Tile
from src.enums import TileType, BridgeType


class TestTileInit:
    def test_default_tile_type_is_grass(self):
        t = Tile(0, 0)
        assert t.tile_type == TileType.GRASS

    def test_position_stored(self):
        t = Tile(3, 7)
        assert t.x == 3
        assert t.y == 7

    def test_all_flags_default_false(self):
        t = Tile(0, 0)
        assert t.is_bank is False
        assert t.is_entry_point is False
        assert t.is_route_road is False
        assert t.is_stop is False
        assert t.is_city_road is False
        assert t.is_garage is False
        assert t.bridge_type is None


class TestTileIsBuildable:
    def test_grass_is_buildable(self):
        t = Tile(0, 0, tile_type=TileType.GRASS)
        assert t.is_buildable is True

    def test_forest_is_buildable(self):
        t = Tile(0, 0, tile_type=TileType.FOREST)
        assert t.is_buildable is True

    def test_road_is_buildable(self):
        t = Tile(0, 0, tile_type=TileType.ROAD)
        assert t.is_buildable is True

    def test_water_is_not_buildable(self):
        t = Tile(0, 0, tile_type=TileType.WATER)
        assert t.is_buildable is False

    def test_city_road_not_buildable_even_if_grass(self):
        t = Tile(0, 0, tile_type=TileType.GRASS, is_city_road=True)
        assert t.is_buildable is False

    def test_track_is_not_buildable(self):
        t = Tile(0, 0, tile_type=TileType.TRACK)
        assert t.is_buildable is False


class TestTileIsTrackBuildable:
    def test_grass_is_track_buildable(self):
        t = Tile(0, 0, tile_type=TileType.GRASS)
        assert t.is_track_buildable is True

    def test_forest_is_track_buildable(self):
        t = Tile(0, 0, tile_type=TileType.FOREST)
        assert t.is_track_buildable is True

    def test_road_is_not_track_buildable_on_tile(self):
        """Tile.is_track_buildable does NOT include ROAD — Grid adds that check."""
        t = Tile(0, 0, tile_type=TileType.ROAD)
        assert t.is_track_buildable is False

    def test_track_is_track_buildable(self):
        t = Tile(0, 0, tile_type=TileType.TRACK)
        assert t.is_track_buildable is True

    def test_water_not_track_buildable(self):
        t = Tile(0, 0, tile_type=TileType.WATER)
        assert t.is_track_buildable is False

    def test_entry_point_check_is_in_grid_not_tile(self):
        """Tile.is_track_buildable does NOT guard entry_point — Grid.is_track_buildable does."""
        t = Tile(0, 0, tile_type=TileType.GRASS, is_entry_point=True)
        assert t.is_track_buildable is True  # Tile itself allows it; Grid rejects it

    def test_city_road_not_track_buildable(self):
        t = Tile(0, 0, tile_type=TileType.TRACK, is_city_road=True)
        assert t.is_track_buildable is False


class TestTileIsDriveable:
    def test_road_tile_is_driveable(self):
        t = Tile(0, 0, tile_type=TileType.ROAD)
        assert t.is_driveable is True

    def test_grass_is_not_driveable(self):
        t = Tile(0, 0, tile_type=TileType.GRASS)
        assert t.is_driveable is False

    def test_water_without_bridge_not_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER)
        assert t.is_driveable is False

    def test_water_with_bridge_is_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER, bridge_type=BridgeType.WOODEN)
        assert t.is_driveable is True

    def test_water_with_stone_bridge_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER, bridge_type=BridgeType.STONE)
        assert t.is_driveable is True


class TestTileIsTrackDriveable:
    def test_track_tile_is_track_driveable(self):
        t = Tile(0, 0, tile_type=TileType.TRACK)
        assert t.is_track_driveable is True

    def test_road_is_not_track_driveable(self):
        t = Tile(0, 0, tile_type=TileType.ROAD)
        assert t.is_track_driveable is False

    def test_water_with_steel_bridge_is_track_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER, bridge_type=BridgeType.STEEL)
        assert t.is_track_driveable is True

    def test_water_with_wooden_bridge_not_track_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER, bridge_type=BridgeType.WOODEN)
        assert t.is_track_driveable is False

    def test_water_no_bridge_not_track_driveable(self):
        t = Tile(0, 0, tile_type=TileType.WATER)
        assert t.is_track_driveable is False


class TestTileIsWater:
    def test_water_tile_is_water(self):
        t = Tile(0, 0, tile_type=TileType.WATER)
        assert t.is_water is True

    def test_grass_is_not_water(self):
        t = Tile(0, 0, tile_type=TileType.GRASS)
        assert t.is_water is False

    def test_road_is_not_water(self):
        t = Tile(0, 0, tile_type=TileType.ROAD)
        assert t.is_water is False
