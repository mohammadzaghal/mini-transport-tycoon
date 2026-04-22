"""Tests for src/models/stop.py"""
import pytest
from src.models.stop import Stop
from src.enums import CargoType


def make_stop(**kwargs):
    defaults = dict(id=1, x=3, y=4, zone_name="Test Zone")
    defaults.update(kwargs)
    return Stop(**defaults)


class TestStopInit:
    def test_fields_stored(self):
        s = make_stop(id=5, x=2, y=7, zone_name="Alpha")
        assert s.id == 5
        assert s.x == 2
        assert s.y == 7
        assert s.zone_name == "Alpha"

    def test_inventory_starts_empty(self):
        s = make_stop()
        assert s.inventory == {}

    def test_total_stock_zero_initially(self):
        s = make_stop()
        assert s.total_stock() == 0.0


class TestStopDeposit:
    def test_deposit_adds_cargo(self):
        s = make_stop()
        s.deposit(CargoType.IRON_ORE, 10.0)
        assert s.stock(CargoType.IRON_ORE) == pytest.approx(10.0)

    def test_deposit_accumulates(self):
        s = make_stop()
        s.deposit(CargoType.FUEL, 5.0)
        s.deposit(CargoType.FUEL, 3.0)
        assert s.stock(CargoType.FUEL) == pytest.approx(8.0)

    def test_deposit_multiple_types(self):
        s = make_stop()
        s.deposit(CargoType.IRON_ORE, 4.0)
        s.deposit(CargoType.AQUATICS, 6.0)
        assert s.total_stock() == pytest.approx(10.0)

    def test_deposit_zero(self):
        s = make_stop()
        s.deposit(CargoType.CRYSTALS, 0.0)
        assert s.stock(CargoType.CRYSTALS) == pytest.approx(0.0)


class TestStopTake:
    def test_take_reduces_stock(self):
        s = make_stop()
        s.deposit(CargoType.IRON_ORE, 10.0)
        taken = s.take(CargoType.IRON_ORE, 4.0)
        assert taken == pytest.approx(4.0)
        assert s.stock(CargoType.IRON_ORE) == pytest.approx(6.0)

    def test_take_more_than_available_returns_what_exists(self):
        s = make_stop()
        s.deposit(CargoType.FUEL, 3.0)
        taken = s.take(CargoType.FUEL, 100.0)
        assert taken == pytest.approx(3.0)
        assert s.stock(CargoType.FUEL) == pytest.approx(0.0)

    def test_take_from_empty_returns_zero(self):
        s = make_stop()
        taken = s.take(CargoType.AQUATICS, 5.0)
        assert taken == pytest.approx(0.0)

    def test_take_exact_amount(self):
        s = make_stop()
        s.deposit(CargoType.CRYSTALS, 7.0)
        taken = s.take(CargoType.CRYSTALS, 7.0)
        assert taken == pytest.approx(7.0)
        assert s.stock(CargoType.CRYSTALS) == pytest.approx(0.0)

    def test_take_does_not_affect_other_types(self):
        s = make_stop()
        s.deposit(CargoType.IRON_ORE, 5.0)
        s.deposit(CargoType.FUEL, 5.0)
        s.take(CargoType.IRON_ORE, 5.0)
        assert s.stock(CargoType.FUEL) == pytest.approx(5.0)


class TestStopStock:
    def test_stock_unknown_type_returns_zero(self):
        s = make_stop()
        assert s.stock(CargoType.TITANIUM_ORE) == pytest.approx(0.0)

    def test_total_stock_sums_all_types(self):
        s = make_stop()
        s.deposit(CargoType.IRON_ORE, 3.0)
        s.deposit(CargoType.ALLOY_ORE, 2.0)
        s.deposit(CargoType.TITANIUM_ORE, 1.0)
        assert s.total_stock() == pytest.approx(6.0)
