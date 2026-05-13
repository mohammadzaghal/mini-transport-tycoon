from __future__ import annotations

import pygame
import pytest

from src.config import BOTTOM_BAR_HEIGHT, TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from src.enums import TileType, TimeSpeed, Tool


pytestmark = pytest.mark.slow


def _key_event(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def _click_events(x: int, y: int) -> list[pygame.event.Event]:
    return [
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (x, y)}),
        pygame.event.Event(pygame.MOUSEBUTTONUP,   {"button": 1, "pos": (x, y)}),
    ]


def _grid_to_screen(game, gx: int, gy: int) -> tuple[int, int]:
    sx = gx * TILE_SIZE - game.camera.x + TILE_SIZE // 2
    sy = gy * TILE_SIZE - game.camera.y + TILE_SIZE // 2
    return sx, sy


def _find_grass_tile(game, exclude: set | None = None) -> tuple[int, int]:
    exclude = exclude or set()
    for t in game.grid.iter_tiles():
        if t.tile_type != TileType.GRASS:
            continue
        if t.is_city_road or t.is_entry_point or t.is_stop:
            continue
        if (t.x, t.y) in exclude:
            continue
        sx, sy = _grid_to_screen(game, t.x, t.y)
        if 0 <= sx < WINDOW_WIDTH and 0 <= sy < WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT:
            return t.x, t.y
    raise AssertionError("no on-screen grass tile found")


class TestSmoke:
    def test_game_constructs(self, seeded_game):
        g = seeded_game
        assert g.company.money > 0
        assert g.time_speed == TimeSpeed.NORMAL
        assert g.tool == Tool.NONE
        assert len(g.facilities) >= 1
        assert len(g.city_growth._points) >= 1

    def test_ticks_without_crashing(self, seeded_game):
        g = seeded_game
        for _ in range(60):
            assert g.tick([]) is True

    def test_draw_populates_screen(self, seeded_game, screen):
        g = seeded_game
        g.draw()
        samples = [screen.get_at((x, y)) for x, y in
                   [(50, 50), (640, 300), (1000, 200)]]
        assert any(s[:3] != (0, 0, 0) for s in samples)


class TestKeyboardInput:
    @pytest.mark.parametrize("key,expected", [
        (pygame.K_r, Tool.ROAD),
        (pygame.K_t, Tool.TRACK),
        (pygame.K_b, Tool.BULLDOZE),
        (pygame.K_g, Tool.GARAGE),
        (pygame.K_k, Tool.BRIDGE),
    ])
    def test_hotkey_switches_tool(self, seeded_game, key, expected):
        seeded_game.tick([_key_event(key)])
        assert seeded_game.tool == expected

    def test_escape_cancels_tool(self, seeded_game):
        seeded_game.tick([_key_event(pygame.K_r)])
        assert seeded_game.tool == Tool.ROAD
        seeded_game.tick([_key_event(pygame.K_ESCAPE)])
        assert seeded_game.tool == Tool.NONE

    @pytest.mark.parametrize("key,expected", [
        (pygame.K_1, TimeSpeed.PAUSE),
        (pygame.K_2, TimeSpeed.NORMAL),
        (pygame.K_3, TimeSpeed.FAST),
        (pygame.K_4, TimeSpeed.VERY_FAST),
    ])
    def test_speed_hotkeys(self, seeded_game, key, expected):
        seeded_game.tick([_key_event(key)])
        assert seeded_game.time_speed == expected

    def test_paused_game_does_not_advance_time(self, seeded_game):
        seeded_game.tick([_key_event(pygame.K_1)])
        before = seeded_game.game_time
        for _ in range(30):
            seeded_game.tick([])
        assert seeded_game.game_time == pytest.approx(before)

    def test_minimap_toggle(self, seeded_game):
        assert seeded_game._show_minimap is True
        seeded_game.tick([_key_event(pygame.K_m)])
        assert seeded_game._show_minimap is False
        seeded_game.tick([_key_event(pygame.K_m)])
        assert seeded_game._show_minimap is True


class TestMouseRoadBuilding:
    def test_click_grass_with_road_tool_paves_it(self, seeded_game):
        g = seeded_game
        gx, gy = _find_grass_tile(g)
        money_before = g.company.money
        g.tool = Tool.ROAD
        g.tick(_click_events(*_grid_to_screen(g, gx, gy)))
        tile = g.grid.get_tile(gx, gy)
        assert tile.tile_type == TileType.ROAD
        assert g.company.money < money_before

    def test_click_without_tool_does_not_pave(self, seeded_game):
        g = seeded_game
        gx, gy = _find_grass_tile(g)
        g.tool = Tool.NONE
        g.tick(_click_events(*_grid_to_screen(g, gx, gy)))
        assert g.grid.get_tile(gx, gy).tile_type == TileType.GRASS

    def test_road_cost_is_deducted(self, seeded_game):
        from src.config import ROAD_COST
        g = seeded_game
        gx, gy = _find_grass_tile(g)
        money_before = g.company.money
        g.tool = Tool.ROAD
        g.tick(_click_events(*_grid_to_screen(g, gx, gy)))
        assert g.company.money == money_before - ROAD_COST


class TestRendering:
    def test_minimap_paints_something(self, seeded_game, screen):
        from src.render.minimap import MM_X, MM_Y, MM_W, MM_H
        seeded_game.draw()
        pts = [(MM_X + 5, MM_Y + 5),
               (MM_X + MM_W - 6, MM_Y + 5),
               (MM_X + 5, MM_Y + MM_H - 6),
               (MM_X + MM_W // 2, MM_Y + MM_H // 2)]
        colours = [tuple(screen.get_at(p))[:3] for p in pts]
        assert any(c != (0, 0, 0) for c in colours)

    def test_road_tile_changes_pixel_after_paving(self, seeded_game, screen):
        g = seeded_game
        gx, gy = _find_grass_tile(g)
        sx, sy = _grid_to_screen(g, gx, gy)
        g.draw()
        before = tuple(screen.get_at((sx, sy)))[:3]
        g.tool = Tool.ROAD
        g.tick(_click_events(sx, sy))
        g.draw()
        after = tuple(screen.get_at((sx, sy)))[:3]
        assert before != after


class TestScriptedScenario:
    def test_build_three_roads_and_advance_time(self, seeded_game):
        g = seeded_game
        g.tick([_key_event(pygame.K_r)])
        assert g.tool == Tool.ROAD

        paved = set()
        for _ in range(3):
            gx, gy = _find_grass_tile(g, exclude=paved)
            g.tick(_click_events(*_grid_to_screen(g, gx, gy)))
            paved.add((gx, gy))

        for x, y in paved:
            assert g.grid.get_tile(x, y).tile_type == TileType.ROAD

        g.tick([_key_event(pygame.K_ESCAPE)])
        g.tick([_key_event(pygame.K_4)])
        time_before = g.game_time
        for _ in range(120):
            assert g.tick([]) is True
        assert g.game_time > time_before

    def test_no_vehicle_leaves_the_grid(self, seeded_game):
        g = seeded_game
        for _ in range(120):
            g.tick([])
        for v in g.vehicles:
            assert 0 <= v.x < g.grid.width
            assert 0 <= v.y < g.grid.height
