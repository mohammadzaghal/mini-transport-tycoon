from __future__ import annotations

import pygame

from src.config import (
    BOTTOM_BAR_HEIGHT, TILE_SIZE,
    WINDOW_HEIGHT, WINDOW_WIDTH,
)
from src.enums import TileType
from src.models.grid import Grid


TILE_COLORS = {
    TileType.GRASS:    (163,  71,  31),
    TileType.FOREST:   (126,  47,  31),
    TileType.ROAD:     (138, 120, 104),
    TileType.CITY:     (216,  92, 157),
    TileType.FACILITY: (224, 104,  32),
}

ROUTE_ROAD_COLOR = (176, 148, 90)
ENTRY_POINT_COLOR = (20, 200, 155)


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _tile_color(tile) -> tuple:
    if tile.is_entry_point:
        return ENTRY_POINT_COLOR
    if tile.tile_type == TileType.ROAD and tile.is_route_road:
        return ROUTE_ROAD_COLOR
    return TILE_COLORS.get(tile.tile_type, (30, 30, 30))


class MapRenderer:
    def __init__(self) -> None:
        self._map_surface: pygame.Surface | None = None
        self._map_w = 0
        self._map_h = 0
        self._bank_font: pygame.font.Font | None = None

    def _get_bank_font(self) -> pygame.font.Font:
        if self._bank_font is None:
            self._bank_font = pygame.font.SysFont("segoeui", 14, bold=True)
        return self._bank_font

    def build_map_image(self, grid: Grid) -> None:
        self._map_w = grid.width  * TILE_SIZE
        self._map_h = grid.height * TILE_SIZE
        self._map_surface = pygame.Surface((self._map_w, self._map_h))
        for tile in grid.iter_tiles():
            color = _tile_color(tile)
            x0 = tile.x * TILE_SIZE
            y0 = tile.y * TILE_SIZE
            pygame.draw.rect(self._map_surface, color, (x0, y0, TILE_SIZE, TILE_SIZE))

    def update_tile(self, x: int, y: int, tile) -> None:
        if self._map_surface is None:
            return
        color = _tile_color(tile)
        x0 = x * TILE_SIZE
        y0 = y * TILE_SIZE
        pygame.draw.rect(self._map_surface, color, (x0, y0, TILE_SIZE, TILE_SIZE))

    def draw(self, screen: pygame.Surface, grid: Grid, camera, routes, vehicles, hover_tile=None) -> None:
        screen.fill((14, 8, 22))

        if self._map_surface is not None:
            screen.blit(self._map_surface, (-camera.x, -camera.y))

        visible_left   = max(0, camera.x // TILE_SIZE)
        visible_top    = max(0, camera.y // TILE_SIZE)
        visible_right  = min(grid.width,  (camera.x + WINDOW_WIDTH) // TILE_SIZE + 2)
        visible_bottom = min(grid.height, (camera.y + WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT) // TILE_SIZE + 2)

        for y in range(visible_top, visible_bottom):
            for x in range(visible_left, visible_right):
                tile = grid.get_tile(x, y)
                if tile is None:
                    continue

                sx = x * TILE_SIZE - camera.x
                sy = y * TILE_SIZE - camera.y

                if tile.tile_type == TileType.FOREST:
                    self._draw_trees(screen, sx, sy, tile.tree_count)

                if tile.is_entry_point:
                    self._draw_entry_marker(screen, sx, sy)

                if tile.is_bank:
                    self._draw_bank_marker(screen, sx, sy)

                if hover_tile == (x, y):
                    pygame.draw.rect(
                        screen, (255, 231, 163),
                        (sx + 1, sy + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2,
                    )

        self._draw_vehicles(screen, camera, vehicles)

   