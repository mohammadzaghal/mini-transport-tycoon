from __future__ import annotations

import pygame
from src.enums import TileType
from src.config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, BOTTOM_BAR_HEIGHT

MM_W = 180
MM_H = int(MM_W * MAP_HEIGHT / MAP_WIDTH)
MM_X = WINDOW_WIDTH - MM_W - 10
MM_Y = 10

_MM_COLORS = {
    TileType.GRASS:    (185, 100, 55),
    TileType.FOREST:   (140,  70, 35),
    TileType.ROAD:     (200, 160, 110),
    TileType.TRACK:    (120, 100,  75),
    TileType.CITY:     (150, 175, 210),
    TileType.FACILITY: (220, 175,  80),
    TileType.WATER:    (190, 215, 235),
}
_MM_STOP_COLOR  = (255, 230, 50)
_MM_VEH_COLOR   = (255, 80, 80)
_MM_VIEWPORT    = (255, 255, 255)

class Minimap:
    def __init__(self) -> None:
        self._surface: pygame.Surface | None = None
        self._dirty = True

    def invalidate(self) -> None:
        self._dirty = True

    def build(self, grid) -> None:
        self._surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        for tile in grid.iter_tiles():
            c = _MM_COLORS.get(tile.tile_type, (50, 50, 50))
            if tile.is_stop:
                c = _MM_STOP_COLOR
            self._surface.set_at((tile.x, tile.y), c)
        self._dirty = False

    def update_tile(self, x: int, y: int, tile) -> None:
        if self._surface is None:
            return
        c = _MM_COLORS.get(tile.tile_type, (50, 50, 50))
        if tile.is_stop:
            c = _MM_STOP_COLOR
        self._surface.set_at((x, y), c)

    def draw(self, screen: pygame.Surface, camera, vehicles: list, stops: list) -> None:
        if self._surface is None:
            return

        scaled = pygame.transform.scale(self._surface, (MM_W, MM_H))

        scale_x = MM_W / MAP_WIDTH
        scale_y = MM_H / MAP_HEIGHT
        for v in vehicles:
            px = int(v.x * scale_x)
            py = int(v.y * scale_y)
            if 0 <= px < MM_W and 0 <= py < MM_H:
                pygame.draw.circle(scaled, _MM_VEH_COLOR, (px, py), 2)

        pygame.draw.rect(scaled, (80, 80, 80), (0, 0, MM_W, MM_H), 1)

        vp_x = int(camera.x / TILE_SIZE * scale_x)
        vp_y = int(camera.y / TILE_SIZE * scale_y)
        vp_w = int(camera.view_width / TILE_SIZE * scale_x)
        vp_h = int((camera.view_height) / TILE_SIZE * scale_y)
        pygame.draw.rect(scaled, _MM_VIEWPORT, (vp_x, vp_y, vp_w, vp_h), 1)

        pygame.draw.rect(screen, (10, 10, 20), (MM_X - 2, MM_Y - 2, MM_W + 4, MM_H + 4))
        screen.blit(scaled, (MM_X, MM_Y))

    def handle_click(self, screen_x: int, screen_y: int, camera) -> bool:
        if MM_X <= screen_x <= MM_X + MM_W and MM_Y <= screen_y <= MM_Y + MM_H:
            rel_x = (screen_x - MM_X) / MM_W
            rel_y = (screen_y - MM_Y) / MM_H
            new_cx = int(rel_x * MAP_WIDTH * TILE_SIZE - camera.view_width // 2)
            new_cy = int(rel_y * MAP_HEIGHT * TILE_SIZE - camera.view_height // 2)
            camera.x = new_cx
            camera.y = new_cy
            camera.clamp()
            return True
        return False
