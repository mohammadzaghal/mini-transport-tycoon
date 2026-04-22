"""Tests for src/engine/city_growth.py"""
import pytest
from unittest.mock import MagicMock

from src.engine.city_growth import CityGrowthManager
from src.models.grid import Grid
from src.enums import TileType
from src.config import CITY_GROWTH_POINTS_PER_DELIVERY, CITY_GROWTH_THRESHOLD


def make_manager():
    return CityGrowthManager()


def make_city_grid():
    """3x3 grid with centre tile as CITY zone."""
    g = Grid(5, 5)
    tile = g.get_tile(2, 2)
    tile.tile_type = TileType.CITY
    tile.zone_name = "TestCity"
    return g


class TestCityGrowthManagerRegister:
    def test_register_adds_city(self):
        m = make_manager()
        m.register_city("Alpha", 5, 5)
        assert m.points("Alpha") == 0.0

    def test_register_multiple_cities(self):
        m = make_manager()
        m.register_city("Alpha", 5, 5)
        m.register_city("Beta", 10, 10)
        assert m.points("Alpha") == 0.0
        assert m.points("Beta") == 0.0

    def test_register_does_not_reset_existing_points(self):
        """Registering a city twice should not wipe its points (setdefault)."""
        m = make_manager()
        m.register_city("Alpha", 5, 5)
        m.on_delivery("Alpha")
        m.register_city("Alpha", 5, 5)  # second call
        assert m.points("Alpha") == CITY_GROWTH_POINTS_PER_DELIVERY

    def test_unknown_city_points_zero(self):
        m = make_manager()
        assert m.points("NoSuchCity") == 0.0


class TestCityGrowthOnDelivery:
    def test_delivery_adds_points(self):
        m = make_manager()
        m.register_city("Alpha", 5, 5)
        m.on_delivery("Alpha")
        assert m.points("Alpha") == CITY_GROWTH_POINTS_PER_DELIVERY

    def test_multiple_deliveries_accumulate(self):
        m = make_manager()
        m.register_city("Alpha", 5, 5)
        m.on_delivery("Alpha")
        m.on_delivery("Alpha")
        assert m.points("Alpha") == CITY_GROWTH_POINTS_PER_DELIVERY * 2

    def test_delivery_to_unknown_city_does_nothing(self):
        """Error path: delivery to unregistered city must not crash."""
        m = make_manager()
        m.on_delivery("Ghost City")   # must not raise

    def test_delivery_only_affects_correct_city(self):
        m = make_manager()
        m.register_city("Alpha", 0, 0)
        m.register_city("Beta", 5, 5)
        m.on_delivery("Alpha")
        assert m.points("Beta") == 0.0


class TestCityGrowthTick:
    def test_tick_triggers_expansion_when_threshold_met(self):
        m = make_manager()
        g = make_city_grid()
        m.register_city("TestCity", 2, 2)
        renderer = MagicMock()
        # Push points over threshold
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer)
        # Points should be reduced (spent on expansion)
        assert m.points("TestCity") < CITY_GROWTH_THRESHOLD

    def test_tick_does_not_trigger_below_threshold(self):
        m = make_manager()
        g = make_city_grid()
        m.register_city("TestCity", 2, 2)
        renderer = MagicMock()
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD - 1
        m.tick(g, renderer)
        assert m.points("TestCity") == CITY_GROWTH_THRESHOLD - 1

    def test_tick_calls_renderer_update_on_expansion(self):
        m = make_manager()
        g = make_city_grid()
        m.register_city("TestCity", 2, 2)
        renderer = MagicMock()
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer)
        assert renderer.update_tile.called

    def test_tick_with_no_registered_cities_does_nothing(self):
        m = make_manager()
        g = make_city_grid()
        renderer = MagicMock()
        m.tick(g, renderer)   # must not raise

    def test_tick_with_minimap_calls_minimap_update(self):
        m = make_manager()
        g = make_city_grid()
        renderer = MagicMock()
        minimap = MagicMock()
        m.register_city("TestCity", 2, 2)
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer, minimap)
        assert minimap.update_tile.called

    def test_expansion_marks_neighbour_tiles(self):
        """After expansion, a neighbour of the city tile should get a zone name."""
        m = make_manager()
        g = make_city_grid()
        m.register_city("TestCity", 2, 2)
        renderer = MagicMock()
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer)
        neighbours = g.neighbors4(2, 2)
        expanded = [n for n in neighbours if n.zone_name == "TestCity"]
        assert len(expanded) > 0

    def test_expansion_sets_correct_tile_types(self):
        """Expanded tiles should be CITY or ROAD (city road), never GRASS."""
        m = make_manager()
        g = make_city_grid()
        m.register_city("TestCity", 2, 2)
        renderer = MagicMock()
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer)
        for tile in g.iter_tiles():
            if tile.zone_name == "TestCity":
                assert tile.tile_type in {TileType.CITY, TileType.ROAD}

    def test_no_expansion_if_no_adjacent_empty_tiles(self):
        """Edge: city surrounded only by non-expandable tiles → no crash."""
        m = make_manager()
        g = Grid(3, 3)
        # Surround centre with water
        for tile in g.iter_tiles():
            tile.tile_type = TileType.WATER
        centre = g.get_tile(1, 1)
        centre.tile_type = TileType.CITY
        centre.zone_name = "TestCity"
        m.register_city("TestCity", 1, 1)
        renderer = MagicMock()
        m._points["TestCity"] = CITY_GROWTH_THRESHOLD
        m.tick(g, renderer)  # must not raise
        renderer.update_tile.assert_not_called()
