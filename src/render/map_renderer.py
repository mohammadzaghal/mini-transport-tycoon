from __future__ import annotations

import pygame

from src.config import BOTTOM_BAR_HEIGHT, TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from src.enums import TileType
from src.models.grid import Grid
from src.assets.sprites import SpriteCache, TILE, _hex_to_rgb
from src.ui.fonts import font_map


_FALLBACK = {
    TileType.GRASS:    (185, 100, 55),
    TileType.FOREST:   (140,  70, 35),
    TileType.ROAD:     (155, 120, 80),
    TileType.TRACK:    (100,  70, 50),                            
    TileType.CITY:     (170, 178, 195),
    TileType.FACILITY: (80,   75, 90),
    TileType.WATER:    (170, 195, 220),
}

ROUTE_ROAD_COLOR  = (220, 170, 60)
ENTRY_POINT_COLOR = (  0, 210, 200)

_FAC_ABBR = {
    "North Mine":  "ORE",
    "South Mine":  "ORE",
    "Fuel Rig":    "FUEL",
    "Aqua Dome N": "H2O",
    "Aqua Dome E": "H2O",
    "Aqua Dome S": "H2O",
    "Crystal Lab": "CRYS",
}


def _tile_color(tile) -> tuple:
    if tile.is_entry_point:
        return ENTRY_POINT_COLOR
    if tile.tile_type == TileType.ROAD and tile.is_route_road:
        return ROUTE_ROAD_COLOR
    return _FALLBACK.get(tile.tile_type, (30, 30, 30))


class MapRenderer:
    def __init__(self) -> None:
        self._map_surface: pygame.Surface | None = None
        self._map_w = 0
        self._map_h = 0
        self._bank_font: pygame.font.Font | None = None
        self._stop_font: pygame.font.Font | None = None
        self._label_font: pygame.font.Font | None = None
        self._sprites: SpriteCache | None = None

    def _get_bank_font(self) -> pygame.font.Font:
        if self._bank_font is None:
            self._bank_font = font_map(14, bold=True)
        return self._bank_font

    def _get_stop_font(self) -> pygame.font.Font:
        if self._stop_font is None:
            self._stop_font = font_map(12, bold=True)
        return self._stop_font

    def _get_label_font(self) -> pygame.font.Font:
        if self._label_font is None:
            self._label_font = font_map(10, bold=True)
        return self._label_font

    def _get_sprites(self) -> SpriteCache:
        if self._sprites is None:
            self._sprites = SpriteCache.get()
            self._sprites.build()
        return self._sprites            