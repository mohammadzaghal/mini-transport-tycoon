"""Tests for src/models/facility.py"""
import pytest
from src.models.facility import Facility
from src.enums import CargoType, FacilityType
from src.config import FACILITY_MAX_STOCK


def make_mine():
    return Facility(name="North Mine", fac_type=FacilityType.ORE_MINE, x=5, y=5)

def make_fuel_rig():
    return Facility(name="Fuel Rig", fac_type=FacilityType.FUEL_RIG, x=10, y=10)

def make_aqua_dome():
    return Facility(name="Aqua Dome N", fac_type=FacilityType.AQUA_DOME, x=2, y=2)


class TestFacilityInit:
    def test_fields_stored(self):
        f = make_mine()
        assert f.name == "North Mine"
        assert f.fac_type == FacilityType.ORE_MINE
        assert f.x == 5
        assert f.y == 5

    def test_ore_mine_initialises_inventory_keys(self):
        f = make_mine()
        assert CargoType.IRON_ORE in f.inventory
        assert CargoType.ALLOY_ORE in f.inventory
        assert CargoType.TITANIUM_ORE in f.inventory

    def test_fuel_rig_initialises_fuel_key(self):
        f = make_fuel_rig()
        assert CargoType.FUEL in f.inventory

    def test_initial_stock_is_zero(self):
        f = make_mine()
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(0.0)


class TestFacilityTick:
    def test_tick_produces_cargo(self):
        f = make_mine()
        f.tick(10.0)
        assert f.stock(CargoType.IRON_ORE) > 0.0

    def test_tick_does_not_exceed_max_stock(self):
        f = make_mine()
        f.inventory[CargoType.IRON_ORE] = FACILITY_MAX_STOCK
        f.tick(100.0)
        assert f.stock(CargoType.IRON_ORE) <= FACILITY_MAX_STOCK

    def test_tick_accumulates_over_time(self):
        f = make_fuel_rig()
        f.tick(1.0)
        after_1 = f.stock(CargoType.FUEL)
        f.tick(1.0)
        after_2 = f.stock(CargoType.FUEL)
        assert after_2 > after_1

    def test_zero_dt_tick_produces_nothing(self):
        f = make_mine()
        f.tick(0.0)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(0.0)

    def test_tick_caps_at_max_stock(self):
        f = make_aqua_dome()
        f.tick(99999.0)
        assert f.stock(CargoType.AQUATICS) == pytest.approx(FACILITY_MAX_STOCK)


class TestFacilityGive:
    def test_give_reduces_stock(self):
        f = make_mine()
        f.inventory[CargoType.IRON_ORE] = 50.0
        taken = f.give(CargoType.IRON_ORE, 20.0)
        assert taken == pytest.approx(20.0)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(30.0)

    def test_give_cannot_exceed_available(self):
        f = make_mine()
        f.inventory[CargoType.IRON_ORE] = 5.0
        taken = f.give(CargoType.IRON_ORE, 100.0)
        assert taken == pytest.approx(5.0)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(0.0)

    def test_give_from_empty_returns_zero(self):
        f = make_mine()
        taken = f.give(CargoType.IRON_ORE, 10.0)
        assert taken == pytest.approx(0.0)

    def test_give_zero(self):
        f = make_mine()
        f.inventory[CargoType.IRON_ORE] = 10.0
        taken = f.give(CargoType.IRON_ORE, 0.0)
        assert taken == pytest.approx(0.0)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(10.0)


class TestFacilityReceive:
    def test_receive_adds_stock(self):
        f = make_mine()
        f.receive(CargoType.IRON_ORE, 30.0)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(30.0)

    def test_receive_capped_at_max(self):
        f = make_mine()
        f.receive(CargoType.IRON_ORE, FACILITY_MAX_STOCK + 9999)
        assert f.stock(CargoType.IRON_ORE) == pytest.approx(FACILITY_MAX_STOCK)

    def test_receive_accumulates(self):
        f = make_fuel_rig()
        f.receive(CargoType.FUEL, 10.0)
        f.receive(CargoType.FUEL, 10.0)
        assert f.stock(CargoType.FUEL) == pytest.approx(20.0)


class TestFacilityProperties:
    def test_produces_returns_correct_types(self):
        f = make_mine()
        assert CargoType.IRON_ORE in f.produces

    def test_consumes_empty_for_mine(self):
        f = make_mine()
        assert f.consumes == {}

    def test_stock_unknown_type_returns_zero(self):
        f = make_fuel_rig()
        assert f.stock(CargoType.CRYSTALS) == pytest.approx(0.0)
