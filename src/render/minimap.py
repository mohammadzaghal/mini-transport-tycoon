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

