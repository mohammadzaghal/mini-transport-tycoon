"""Tests for src/engine/camera.py"""
import pytest
from src.engine.camera import Camera


def make_camera(map_w=1000, map_h=800, view_w=400, view_h=300):
    return Camera(map_width_px=map_w, map_height_px=map_h,
                  view_width=view_w, view_height=view_h)


class TestCameraInit:
    def test_starts_at_origin(self):
        c = make_camera()
        assert c.x == 0
        assert c.y == 0

    def test_dimensions_stored(self):
        c = make_camera(map_w=2000, map_h=1500, view_w=800, view_h=600)
        assert c.map_width_px == 2000
        assert c.map_height_px == 1500
        assert c.view_width == 800
        assert c.view_height == 600


class TestCameraMove:
    def test_move_right(self):
        c = make_camera()
        c.move(100, 0)
        assert c.x == 100

    def test_move_down(self):
        c = make_camera()
        c.move(0, 50)
        assert c.y == 50

    def test_move_clamps_at_max_x(self):
        c = make_camera(map_w=1000, view_w=400)
        c.move(9999, 0)
        assert c.x == 600  # 1000 - 400

    def test_move_clamps_at_max_y(self):
        c = make_camera(map_h=800, view_h=300)
        c.move(0, 9999)
        assert c.y == 500  # 800 - 300

    def test_move_clamps_at_min_zero(self):
        c = make_camera()
        c.move(-9999, -9999)
        assert c.x == 0
        assert c.y == 0

    def test_cumulative_moves(self):
        c = make_camera()
        c.move(100, 0)
        c.move(50, 0)
        assert c.x == 150

    def test_move_left_from_position(self):
        c = make_camera()
        c.move(200, 0)
        c.move(-100, 0)
        assert c.x == 100


class TestCameraClamp:
    def test_clamp_does_not_change_valid_position(self):
        c = make_camera(map_w=1000, view_w=400)
        c.x = 300
        c.clamp()
        assert c.x == 300

    def test_clamp_fixes_negative(self):
        c = make_camera()
        c.x = -50
        c.clamp()
        assert c.x == 0

    def test_clamp_fixes_overflow(self):
        c = make_camera(map_w=1000, view_w=400)
        c.x = 9999
        c.clamp()
        assert c.x == 600

    def test_clamp_when_map_smaller_than_view(self):
        """Edge case: map fits entirely in view — max offset should be 0."""
        c = Camera(map_width_px=200, map_height_px=200, view_width=400, view_height=400)
        c.x = 50
        c.clamp()
        assert c.x == 0


class TestCameraCoordinates:
    def test_world_to_screen_at_origin(self):
        c = make_camera()
        sx, sy = c.world_to_screen(100, 200)
        assert sx == 100
        assert sy == 200

    def test_world_to_screen_with_offset(self):
        c = make_camera()
        c.x = 50
        c.y = 30
        sx, sy = c.world_to_screen(100, 100)
        assert sx == 50
        assert sy == 70

    def test_screen_to_world_at_origin(self):
        c = make_camera()
        wx, wy = c.screen_to_world(100, 200)
        assert wx == 100
        assert wy == 200

    def test_screen_to_world_with_offset(self):
        c = make_camera()
        c.x = 80
        c.y = 40
        wx, wy = c.screen_to_world(100, 100)
        assert wx == 180
        assert wy == 140

    def test_round_trip_consistency(self):
        """screen_to_world(world_to_screen(p)) == p"""
        c = make_camera()
        c.x = 123
        c.y = 456
        wx, wy = 300, 250
        sx, sy = c.world_to_screen(wx, wy)
        rx, ry = c.screen_to_world(sx, sy)
        assert rx == wx
        assert ry == wy
