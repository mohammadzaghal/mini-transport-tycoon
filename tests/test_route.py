"""Tests for src/models/route.py"""
import pytest
from src.models.route import Route


def make_route(**kwargs):
    defaults = dict(
        id=1,
        name="Route 1",
        endpoint_a=(0, 0),
        endpoint_b=(5, 0),
        path=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],
        profitable=True,
        path_type="road",
    )
    defaults.update(kwargs)
    return Route(**defaults)


class TestRouteInit:
    def test_fields_stored(self):
        r = make_route(id=7, name="Route 7")
        assert r.id == 7
        assert r.name == "Route 7"

    def test_endpoints_stored(self):
        r = make_route(endpoint_a=(1, 2), endpoint_b=(9, 9))
        assert r.endpoint_a == (1, 2)
        assert r.endpoint_b == (9, 9)

    def test_path_stored(self):
        path = [(0, 0), (1, 0), (2, 0)]
        r = make_route(path=path)
        assert r.path == path

    def test_default_path_empty(self):
        r = Route(id=1, name="R", endpoint_a=(0, 0), endpoint_b=(1, 0))
        assert r.path == []

    def test_profitable_flag(self):
        r = make_route(profitable=True)
        assert r.profitable is True

    def test_not_profitable_by_default(self):
        r = Route(id=1, name="R", endpoint_a=(0, 0), endpoint_b=(1, 0))
        assert r.profitable is False

    def test_path_type_road_default(self):
        r = Route(id=1, name="R", endpoint_a=(0, 0), endpoint_b=(1, 0))
        assert r.path_type == "road"

    def test_path_type_track(self):
        r = make_route(path_type="track")
        assert r.path_type == "track"

    def test_stop_positions_default_empty(self):
        r = make_route()
        assert r.stop_positions == []

    def test_stop_positions_can_be_set(self):
        stops = [(2, 0), (4, 0)]
        r = make_route(stop_positions=stops)
        assert r.stop_positions == stops


class TestRouteEdgeCases:
    def test_same_endpoints_allowed(self):
        """Route model itself does not forbid same endpoints (game.py guards that)."""
        r = make_route(endpoint_a=(3, 3), endpoint_b=(3, 3))
        assert r.endpoint_a == r.endpoint_b

    def test_large_path(self):
        path = [(i, 0) for i in range(100)]
        r = make_route(path=path)
        assert len(r.path) == 100
