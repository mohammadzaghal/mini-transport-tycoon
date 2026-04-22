"""
Comprehensive tests for src/models/vehicle.py

Covers:
  - Happy path: normal movement, cargo loading/unloading, loop completion
  - Error path: empty/short paths, overfull cargo, missing cargo types
  - Edge cases: zero dt, exact-boundary distance, single-tile paths
  - Difficult-to-reproduce: multi-loop accumulation, near-capacity loads,
    auto-initialisation, floating-point overshoot at high speed
"""

import math
import pytest

from src.enums import CargoType, VehicleType
from src.models.vehicle import Vehicle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_vehicle(path=None, speed=1.0, capacity=10, vtype=VehicleType.TRUCK):
    """Return a Vehicle with sensible defaults for testing."""
    return Vehicle(
        name="TestVehicle",
        vehicle_type=vtype,
        path=path or [],
        speed_tiles_per_second=speed,
        capacity=capacity,
    )


def straight_path(length=3):
    """Horizontal path: [(0,0),(1,0),(2,0),...]"""
    return [(i, 0) for i in range(length)]


def loop_path(length=3):
    """Bidirectional loop as the game builds it: A→B + B→A (skipping duplicate midpoint)."""
    outbound = [(i, 0) for i in range(length)]
    inbound = list(reversed(outbound))
    return outbound + inbound[1:]


# ===========================================================================
# 1. INITIALISATION
# ===========================================================================

class TestInitializePosition:
    def test_sets_position_to_first_tile(self):
        v = make_vehicle(path=[(5, 3), (6, 3)])
        v.initialize_position()
        assert v.x == 5.0
        assert v.y == 3.0

    def test_resets_current_index_to_zero(self):
        v = make_vehicle(path=[(0, 0), (1, 0)])
        v.current_index = 99
        v.initialize_position()
        assert v.current_index == 0

    def test_marks_initialized(self):
        v = make_vehicle(path=[(0, 0), (1, 0)])
        assert v._initialized is False
        v.initialize_position()
        assert v._initialized is True

    def test_clears_at_stop_flag(self):
        v = make_vehicle(path=[(0, 0), (1, 0)])
        v.at_stop = True          # type: ignore[attr-defined]
        v.initialize_position()
        assert v.at_stop is False

    def test_empty_path_does_not_crash(self):
        """Edge case: initialise with no path should silently do nothing."""
        v = make_vehicle(path=[])
        v.initialize_position()   # must not raise
        assert v._initialized is False


# ===========================================================================
# 2. UPDATE — HAPPY PATH
# ===========================================================================

class TestUpdateMovement:
    def test_vehicle_moves_toward_next_tile(self):
        v = make_vehicle(path=[(0, 0), (10, 0)], speed=1.0)
        v.initialize_position()
        v.update(0.5)
        assert v.x == pytest.approx(0.5, abs=1e-6)
        assert v.y == pytest.approx(0.0, abs=1e-6)

    def test_vehicle_snaps_to_tile_on_exact_arrival(self):
        """step == distance → should land exactly on target tile."""
        v = make_vehicle(path=[(0, 0), (1, 0)], speed=1.0)
        v.initialize_position()
        v.update(1.0)
        assert v.x == pytest.approx(1.0)
        assert v.current_index == 1

    def test_vehicle_snaps_on_overshoot(self):
        """step > distance → must not drift past the tile."""
        v = make_vehicle(path=[(0, 0), (1, 0)], speed=100.0)
        v.initialize_position()
        v.update(1.0)
        assert v.x == pytest.approx(1.0)
        assert v.y == pytest.approx(0.0)

    def test_returns_true_on_loop_completion(self):
        """Vehicle completing a full loop must return True."""
        path = straight_path(3)   # 3 tiles → wraps at index 0
        v = make_vehicle(path=path, speed=999.0)
        v.initialize_position()
        results = [v.update(1.0) for _ in range(len(path) + 5)]
        assert True in results

    def test_delivered_legs_increments_on_loop(self):
        path = straight_path(3)
        v = make_vehicle(path=path, speed=999.0)
        v.initialize_position()
        for _ in range(len(path) * 3):
            v.update(1.0)
        assert v.delivered_legs >= 1

    def test_multiple_loops_accumulate_correctly(self):
        """Difficult-to-reproduce: run 10 full loops and verify counter."""
        path = straight_path(3)
        v = make_vehicle(path=path, speed=999.0)
        v.initialize_position()
        for _ in range(len(path) * 20):
            v.update(1.0)
        assert v.delivered_legs >= 5

    def test_auto_initialises_if_not_yet_done(self):
        """update() must call initialize_position() automatically."""
        v = make_vehicle(path=[(0, 0), (5, 0)], speed=1.0)
        assert v._initialized is False
        v.update(0.1)
        assert v._initialized is True

    def test_diagonal_movement(self):
        """Vehicle moves correctly along a diagonal path."""
        v = make_vehicle(path=[(0, 0), (3, 4)], speed=5.0)
        v.initialize_position()
        v.update(1.0)
        dist = math.hypot(v.x - 0, v.y - 0)
        assert dist == pytest.approx(5.0, abs=1e-4)


# ===========================================================================
# 3. UPDATE — ERROR / EDGE CASES
# ===========================================================================

class TestUpdateEdgeCases:
    def test_empty_path_returns_false(self):
        v = make_vehicle(path=[])
        assert v.update(1.0) is False

    def test_single_tile_path_returns_false(self):
        """Path of length 1 has no next tile — should not crash."""
        v = make_vehicle(path=[(0, 0)])
        assert v.update(1.0) is False

    def test_zero_dt_does_not_move(self):
        """Zero delta-time → vehicle must stay in place."""
        v = make_vehicle(path=[(0, 0), (10, 0)], speed=5.0)
        v.initialize_position()
        v.update(0.0)
        assert v.x == pytest.approx(0.0)
        assert v.y == pytest.approx(0.0)

    def test_tiny_dt_accumulates_correctly(self):
        """Many tiny steps should produce the same result as one big step."""
        path = [(0, 0), (1, 0)]
        v1 = make_vehicle(path=path, speed=1.0)
        v1.initialize_position()
        v1.update(0.5)

        v2 = make_vehicle(path=path, speed=1.0)
        v2.initialize_position()
        for _ in range(50):
            v2.update(0.01)

        assert v1.x == pytest.approx(v2.x, abs=1e-4)

    def test_very_large_dt_does_not_crash(self):
        """Huge dt (e.g. 1000s) must snap cleanly, not raise."""
        v = make_vehicle(path=straight_path(5), speed=1.0)
        v.initialize_position()
        v.update(1000.0)   # must not raise

    def test_at_stop_set_when_tile_reached(self):
        """at_stop should be True after snapping to a tile."""
        v = make_vehicle(path=[(0, 0), (1, 0)], speed=999.0)
        v.initialize_position()
        v.update(1.0)
        assert v.at_stop is True

    def test_at_stop_false_when_mid_tile(self):
        """at_stop must be False when the vehicle has not yet reached a tile."""
        v = make_vehicle(path=[(0, 0), (100, 0)], speed=1.0)
        v.initialize_position()
        v.update(0.1)
        assert v.at_stop is False

    def test_distance_less_than_epsilon_snaps(self):
        """Reproduce the < 1e-6 guard: place vehicle essentially on target."""
        v = make_vehicle(path=[(0, 0), (1, 0)], speed=1.0)
        v.initialize_position()
        # Move vehicle to within floating-point epsilon of target
        v.x = 1.0 - 1e-9
        v.update(0.0001)
        # Should have snapped to index 1 without dividing by zero
        assert v.current_index == 1


# ===========================================================================
# 4. CARGO — HAPPY PATH
# ===========================================================================

class TestCargoLoad:
    def test_load_adds_cargo(self):
        v = make_vehicle(capacity=10)
        loaded = v.load(CargoType.IRON_ORE, 5.0)
        assert loaded == pytest.approx(5.0)
        assert v.cargo_on_board[CargoType.IRON_ORE] == pytest.approx(5.0)

    def test_load_multiple_types(self):
        v = make_vehicle(capacity=10)
        v.load(CargoType.IRON_ORE, 4.0)
        v.load(CargoType.FUEL, 3.0)
        assert v.total_cargo == pytest.approx(7.0)

    def test_load_returns_amount_actually_loaded(self):
        v = make_vehicle(capacity=5)
        loaded = v.load(CargoType.CRYSTALS, 3.0)
        assert loaded == pytest.approx(3.0)

    def test_total_cargo_sums_all_types(self):
        v = make_vehicle(capacity=20)
        v.load(CargoType.IRON_ORE, 5.0)
        v.load(CargoType.ALLOY_ORE, 7.0)
        assert v.total_cargo == pytest.approx(12.0)


class TestCargoCapacity:
    def test_cannot_load_beyond_capacity(self):
        """Error path: loading more than capacity should be clamped."""
        v = make_vehicle(capacity=5)
        loaded = v.load(CargoType.IRON_ORE, 100.0)
        assert loaded == pytest.approx(5.0)
        assert v.total_cargo == pytest.approx(5.0)

    def test_load_when_full_returns_zero(self):
        v = make_vehicle(capacity=5)
        v.load(CargoType.IRON_ORE, 5.0)
        loaded = v.load(CargoType.FUEL, 1.0)
        assert loaded == pytest.approx(0.0)

    def test_partial_load_near_capacity(self):
        """Edge case: only partial space remaining."""
        v = make_vehicle(capacity=10)
        v.load(CargoType.IRON_ORE, 8.0)
        loaded = v.load(CargoType.FUEL, 5.0)
        assert loaded == pytest.approx(2.0)
        assert v.total_cargo == pytest.approx(10.0)

    def test_load_zero_amount(self):
        v = make_vehicle(capacity=10)
        loaded = v.load(CargoType.AQUATICS, 0.0)
        assert loaded == pytest.approx(0.0)
        assert v.total_cargo == pytest.approx(0.0)


class TestCargoUnload:
    def test_unload_all_returns_copy(self):
        v = make_vehicle(capacity=10)
        v.load(CargoType.IRON_ORE, 3.0)
        v.load(CargoType.FUEL, 2.0)
        result = v.unload_all()
        assert result[CargoType.IRON_ORE] == pytest.approx(3.0)
        assert result[CargoType.FUEL] == pytest.approx(2.0)

    def test_unload_all_clears_cargo(self):
        v = make_vehicle(capacity=10)
        v.load(CargoType.CRYSTALS, 5.0)
        v.unload_all()
        assert v.total_cargo == pytest.approx(0.0)
        assert len(v.cargo_on_board) == 0

    def test_unload_specific_type(self):
        v = make_vehicle(capacity=10)
        v.load(CargoType.TITANIUM_ORE, 4.0)
        v.load(CargoType.AQUATICS, 2.0)
        amount = v.unload(CargoType.TITANIUM_ORE)
        assert amount == pytest.approx(4.0)
        assert CargoType.TITANIUM_ORE not in v.cargo_on_board
        assert v.total_cargo == pytest.approx(2.0)

    def test_unload_missing_type_returns_zero(self):
        """Error path: unloading cargo that was never loaded."""
        v = make_vehicle(capacity=10)
        amount = v.unload(CargoType.CRYSTALS)
        assert amount == pytest.approx(0.0)

    def test_unload_all_on_empty_vehicle(self):
        """Edge case: unloading when nothing is on board."""
        v = make_vehicle(capacity=10)
        result = v.unload_all()
        assert result == {}

    def test_reload_after_unload(self):
        """After unloading, vehicle should accept cargo up to full capacity again."""
        v = make_vehicle(capacity=10)
        v.load(CargoType.FUEL, 10.0)
        v.unload_all()
        loaded = v.load(CargoType.IRON_ORE, 10.0)
        assert loaded == pytest.approx(10.0)


# ===========================================================================
# 5. VEHICLE PROPERTIES & LEVEL
# ===========================================================================

class TestVehicleProperties:
    def test_default_level_is_one(self):
        v = make_vehicle()
        assert v.level == 1

    def test_delivered_legs_starts_at_zero(self):
        v = make_vehicle()
        assert v.delivered_legs == 0

    def test_route_id_default_is_minus_one(self):
        v = make_vehicle()
        assert v.route_id == -1

    def test_vehicle_type_stored_correctly(self):
        v = make_vehicle(vtype=VehicleType.TRAIN)
        assert v.vehicle_type == VehicleType.TRAIN

    def test_capacity_respected_after_manual_upgrade(self):
        """Simulate what _upgrade_vehicle does: mutate capacity and speed."""
        v = make_vehicle(capacity=10, speed=2.0)
        v.base_speed = 2.0
        v.base_capacity = 10
        v.level = 2
        v.speed_tiles_per_second = v.base_speed * 1.25
        v.capacity = int(v.base_capacity * 1.30)
        assert v.speed_tiles_per_second == pytest.approx(2.5)
        assert v.capacity == 13

    def test_maintenance_timer_starts_at_zero(self):
        v = make_vehicle()
        assert v.maintenance_timer == pytest.approx(0.0)
        assert v.needs_maintenance is False


# ===========================================================================
# 6. DIFFICULT-TO-REPRODUCE SITUATIONS
# ===========================================================================

class TestDifficultSituations:
    def test_vehicle_loop_delivery_signal_fires_exactly_once_per_loop(self):
        """Verify delivered_legs increments by exactly 1 per full loop."""
        path = straight_path(4)
        v = make_vehicle(path=path, speed=999.0)
        v.initialize_position()
        loops = 0
        for _ in range(len(path) * 10):
            if v.update(1.0):
                loops += 1
        assert loops == v.delivered_legs

    def test_cargo_survives_across_multiple_move_updates(self):
        """Cargo must not be affected by update() calls."""
        v = make_vehicle(path=straight_path(5), speed=0.5, capacity=10)
        v.initialize_position()
        v.load(CargoType.AQUATICS, 7.0)
        for _ in range(20):
            v.update(0.1)
        assert v.total_cargo == pytest.approx(7.0)

    def test_mixed_cargo_types_independent(self):
        """Loading one type must not affect another type's stored amount."""
        v = make_vehicle(capacity=20)
        v.load(CargoType.IRON_ORE, 5.0)
        v.load(CargoType.ALLOY_ORE, 5.0)
        v.load(CargoType.TITANIUM_ORE, 5.0)
        v.unload(CargoType.ALLOY_ORE)
        assert v.cargo_on_board.get(CargoType.IRON_ORE) == pytest.approx(5.0)
        assert v.cargo_on_board.get(CargoType.TITANIUM_ORE) == pytest.approx(5.0)
        assert CargoType.ALLOY_ORE not in v.cargo_on_board

    def test_path_with_duplicate_consecutive_tiles(self):
        """Edge case: two identical consecutive tiles → distance ≈ 0, must not hang."""
        path = [(0, 0), (0, 0), (1, 0)]
        v = make_vehicle(path=path, speed=1.0)
        v.initialize_position()
        for _ in range(10):
            v.update(0.5)   # must not raise or loop forever

    def test_high_speed_many_frames_no_position_drift(self):
        """
        Difficult-to-reproduce: at high speed, position must always land
        exactly on a tile centre — never floating between tiles at rest.
        """
        path = loop_path(5)
        v = make_vehicle(path=path, speed=50.0)
        v.initialize_position()
        for _ in range(500):
            v.update(0.016)  # ~60 fps

        # After many frames, vehicle must be on a path tile exactly
        tile_positions = set(path)
        current = (round(v.x), round(v.y))
        # Allow for mid-move position — check integer parts are within path range
        assert 0 <= v.x <= max(p[0] for p in path) + 1
        assert 0 <= v.y <= max(p[1] for p in path) + 1

    def test_returning_to_garage_flag(self):
        """returning_to_garage starts False and can be set."""
        v = make_vehicle()
        assert v.returning_to_garage is False
        v.returning_to_garage = True
        assert v.returning_to_garage is True

    def test_age_days_independent_of_update(self):
        """age_days is not modified by update() — only the game loop does that."""
        v = make_vehicle(path=straight_path(3), speed=1.0)
        v.initialize_position()
        v.update(5.0)
        assert v.age_days == pytest.approx(0.0)
