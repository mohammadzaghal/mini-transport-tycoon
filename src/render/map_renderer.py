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

    #for 1–4 trees
    _TREE_POSITIONS = [
        [(16, 14)],
        [(9, 11), (23, 11)],
        [(9, 10), (23, 10), (16, 22)],
        [(9, 10), (23, 10), (9, 22), (23, 22)],
    ]

    def _draw_trees(self, screen: pygame.Surface, x: int, y: int, count: int) -> None:
        count = max(1, min(count, 4))
        for cx, cy in self._TREE_POSITIONS[count - 1]:
            pygame.draw.ellipse(screen, (38, 122, 20),  (x + cx - 6, y + cy - 6, 12, 10))
            pygame.draw.ellipse(screen, (61, 160, 32),  (x + cx - 6, y + cy - 6, 12, 10), 1)
            pygame.draw.ellipse(screen, (74, 184, 48),  (x + cx - 3, y + cy - 5, 4, 3))
            pygame.draw.rect(screen,   (90, 48, 16),   (x + cx - 1, y + cy + 4, 3, 5))

    def _draw_entry_marker(self, screen: pygame.Surface, x: int, y: int) -> None:
        mid = TILE_SIZE // 2
        r = 6
        pts = [
            (x + mid,     y + mid - r),
            (x + mid + r, y + mid),
            (x + mid,     y + mid + r),
            (x + mid - r, y + mid),
        ]
        pygame.draw.polygon(screen, (255, 230, 40), pts)
        pygame.draw.polygon(screen, (200, 140,  0), pts, 1)

    def _draw_bank_marker(self, screen: pygame.Surface, x: int, y: int) -> None:
        font = self._get_bank_font()
        surf = font.render("$", True, (255, 208, 96))
        screen.blit(surf, (
            x + TILE_SIZE // 2 - surf.get_width()  // 2,
            y + TILE_SIZE // 2 - surf.get_height() // 2,
        ))

    def _draw_vehicles(self, screen: pygame.Surface, camera, vehicles) -> None:
        for vehicle in vehicles:
            world_x = int(vehicle.x * TILE_SIZE + TILE_SIZE // 2)
            world_y = int(vehicle.y * TILE_SIZE + TILE_SIZE // 2)
            sx = world_x - camera.x
            sy = world_y - camera.y
            color = _hex_to_rgb(vehicle.color)
            pygame.draw.rect(screen, color, (sx - 9, sy - 7, 18, 14))
            pygame.draw.rect(screen, (255, 255, 255), (sx - 9, sy - 7, 18, 14), 2)
            pygame.draw.circle(screen, (51, 51, 51), (sx - 6, sy + 7), 4)
            pygame.draw.circle(screen, (51, 51, 51), (sx + 6, sy + 7), 4)