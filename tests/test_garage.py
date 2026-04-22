"""Tests for src/models/garage.py"""
import pytest
from src.models.garage import Garage


class TestGarageInit:
    def test_position_stored(self):
        g = Garage(x=4, y=9)
        assert g.x == 4
        assert g.y == 9

    def test_default_capacity(self):
        g = Garage(x=0, y=0)
        assert g.capacity == 6

    def test_custom_capacity(self):
        g = Garage(x=0, y=0, capacity=12)
        assert g.capacity == 12


class TestGaragePos:
    def test_pos_returns_tuple(self):
        g = Garage(x=3, y=7)
        assert g.pos == (3, 7)

    def test_pos_origin(self):
        g = Garage(x=0, y=0)
        assert g.pos == (0, 0)

    def test_pos_large_coords(self):
        g = Garage(x=999, y=888)
        assert g.pos == (999, 888)
