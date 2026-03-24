from __future__ import annotations

import pygame

from src.config import (
    BOTTOM_BAR_HEIGHT,
    MAP_HEIGHT,
    MAP_WIDTH,
    TILE_SIZE,
    TICK_MS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.engine.camera import Camera
from src.engine.map_generator import MapGenerator
from src.enums import TimeSpeed, Tool
from src.models.company import Company
from src.models.grid import Grid
from src.render.map_renderer import MapRenderer
from src.ui.hud import HUD

FPS = 1000 // TICK_MS


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Transport Tycoon")
        self.fullscreen = False
        self.clock = pygame.time.Clock()

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.company = Company("Player Co.", 0)
        self.time_speed = TimeSpeed.NORMAL
        self.tool = Tool.NONE
        self.status_message = "Basic mode (no building/vehicles)."

        self.game_time = 0.0

        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE,
            view_width=WINDOW_WIDTH,
            view_height=WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
        )
        self.renderer = MapRenderer()
        self.hud = HUD()

        MapGenerator(seed=7).generate(self.grid)
        self.renderer.build_map_image(self.grid)

        self._hover_tile = None

        self._drag_start_screen = None
        self._drag_start_camera = None
        self._dragging_map = False
        self._drag_threshold = 8

    def run(self) -> None:
        running = True
        while running:
            dt_ms = self.clock.tick(FPS)
            real_dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._on_left_press(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._on_left_release(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._on_mouse_move(event.pos, bool(event.buttons[0]))
                elif event.type == pygame.MOUSEWHEEL:
                    mods = pygame.key.get_mods()
                    scroll = event.y * 48
                    if mods & pygame.KMOD_SHIFT:
                        self.camera.move(-scroll, 0)
                    else:
                        self.camera.move(0, -scroll)
                elif event.type == pygame.KEYDOWN:
                    self._on_key_down(event.key)

            self._handle_camera_input(real_dt)

            if self.time_speed != TimeSpeed.PAUSE:
                sim_dt = real_dt * self.time_speed.value
                self.update(sim_dt)

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def update(self, dt: float) -> None:
        self.game_time += dt

    def draw(self) -> None:
        self.renderer.draw(
            self.screen, self.grid, self.camera,
            [], [], self._hover_tile,
        )
        self._draw_scrollbars()
        self.hud.draw(
            self.screen,
            money=self.company.money,
            game_time=self.game_time,
            time_speed=self.time_speed,
            tool=self.tool,
            status=self.status_message,
            garage=[],
            vehicles=[],
        )

=    def _draw_scrollbars(self) -> None:
        bar_width = 10
        bar_x = WINDOW_WIDTH - bar_width
        bar_height = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT
        thumb_height = min(bar_height, int(bar_height * self.camera.view_height / self.camera.map_height_px))
        thumb_y = int((bar_height - thumb_height) * self.camera.y / max(1, self.camera.map_height_px - self.camera.view_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, 0, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, thumb_y, bar_width, thumb_height))

        bar_y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT - bar_width
        bar_width_h = WINDOW_WIDTH
        thumb_width = min(bar_width_h, int(bar_width_h * self.camera.view_width / self.camera.map_width_px))
        thumb_x = int((bar_width_h - thumb_width) * self.camera.x / max(1, self.camera.map_width_px - self.camera.view_width))
        pygame.draw.rect(self.screen, (200, 200, 200), (0, bar_y, bar_width_h, bar_width))
        pygame.draw.rect(self.screen, (100, 100, 100), (thumb_x, bar_y, thumb_width, bar_width))

    def _on_left_press(self, pos: tuple) -> None:
        self._drag_start_screen = pos
        self._drag_start_camera = (self.camera.x, self.camera.y)
        self._dragging_map = False

    def _on_mouse_move(self, pos: tuple, left_held: bool) -> None:
        x, y = pos
        if left_held and self._drag_start_screen:
            sx, sy = self._drag_start_screen
            dx, dy = x - sx, y - sy
            if abs(dx) > self._drag_threshold or abs(dy) > self._drag_threshold:
                self._dragging_map = True
            if self._dragging_map:
                cam_x, cam_y = self._drag_start_camera
                self.camera.x = cam_x - dx
                self.camera.y = cam_y - dy
                self.camera.clamp()

    def _on_left_release(self, pos: tuple) -> None:
        self._drag_start_screen = None
        self._dragging_map = False

    def _on_key_down(self, key: int) -> None:
        if key == pygame.K_1:
            self.time_speed = TimeSpeed.PAUSE
        elif key == pygame.K_2:
            self.time_speed = TimeSpeed.NORMAL
        elif key == pygame.K_3:
            self.time_speed = TimeSpeed.FAST
        elif key == pygame.K_4:
            self.time_speed = TimeSpeed.VERY_FAST
        elif key == pygame.K_ESCAPE:
            self.tool = Tool.NONE
        elif key == pygame.K_F11:
            self._toggle_fullscreen()

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

    def _handle_camera_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        step = int(500 * dt)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera.move(-step, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera.move(step, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera.move(0, -step)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera.move(0, step)

    def _build_road(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if not self.grid.is_road_buildable(x, y):
            self.status_message = "Can only build roads on grass or forest tiles."
            return
        cost = ROAD_COST + (FOREST_CLEAR_COST if tile.tile_type == TileType.FOREST else 0)
        if not self.company.spend(cost):
            self.status_message = "Not enough credits to build road (need ${}).".format(cost)
            return
        tile.tile_type = TileType.ROAD
        tile.tree_count = 0
        self.renderer.update_tile(x, y, tile)
        self.status_message = "Road built at ({},{}) for ${}.".format(x, y, cost)

    def _bulldoze(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type == TileType.ROAD and not tile.is_entry_point:
            for route in self.routes:
                if (x, y) in route.path:
                    self._dissolve_route(route)
                    return
            tile.tile_type = TileType.GRASS
            tile.is_route_road = False
            self.renderer.update_tile(x, y, tile)
            self.status_message = "Road removed at ({},{}).".format(x, y)