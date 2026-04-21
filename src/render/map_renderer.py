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
    TileType.TRACK:    (100,  70, 50),                            # v1.1 #3
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

    def _tile_sprite_key(self, tile) -> str | None:
        """Return sprite cache key for a tile, or None to use fallback."""
        if tile.is_entry_point:
            return "road_entry"
        if tile.is_garage:
            return "garage"
        if tile.bridge_type is not None:
            suffix = "_route" if tile.is_route_road else ""
            return f"bridge_{tile.bridge_type.name}{suffix}"
        if tile.tile_type == TileType.WATER:
            return "water"
        if tile.tile_type == TileType.GRASS:
            return "grass"
        if tile.tile_type == TileType.FOREST:
            return "forest"
        if tile.tile_type == TileType.ROAD:
            return "road_route" if tile.is_route_road else "road"
        if tile.tile_type == TileType.TRACK:                      # v1.1 #3
            return "track_route" if tile.is_route_road else "track"
        if tile.tile_type == TileType.CITY:
            return "city_bank" if tile.is_bank else "city"
        if tile.tile_type == TileType.FACILITY:
            if tile.facility_ref is not None:
                return f"fac_{tile.facility_ref.fac_type.name}"
        return None

    def build_map_image(self, grid: Grid) -> None:
        sp = self._get_sprites()
        self._map_w = grid.width  * TILE_SIZE
        self._map_h = grid.height * TILE_SIZE
        self._map_surface = pygame.Surface((self._map_w, self._map_h))
        for tile in grid.iter_tiles():
            self._paint_tile(tile)

    def _paint_tile(self, tile) -> None:
        if self._map_surface is None:
            return
        x0 = tile.x * TILE_SIZE
        y0 = tile.y * TILE_SIZE
        sp = self._get_sprites()
        key = self._tile_sprite_key(tile)
        surf = sp.tile(key) if key else None
        if surf is not None:
            self._map_surface.blit(surf, (x0, y0))
        else:
            color = _tile_color(tile)
            pygame.draw.rect(self._map_surface, color, (x0, y0, TILE_SIZE, TILE_SIZE))

    def update_tile(self, x: int, y: int, tile) -> None:
        if self._map_surface is None:
            return
        self._paint_tile(tile)

    def draw(
        self,
        screen: pygame.Surface,
        grid: Grid,
        camera,
        routes,
        vehicles,
        hover_tile=None,
        stops=None,
    ) -> None:
        screen.fill((10, 6, 4))  # Dark Mars background

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
                    self._draw_rocks(screen, sx, sy)

                if tile.is_entry_point:
                    self._draw_entry_marker(screen, sx, sy)

                if tile.is_bank:
                    self._draw_bank_marker(screen, sx, sy)

                if tile.is_stop:
                    self._draw_stop_marker(screen, sx, sy)

                if tile.is_garage:
                    self._draw_garage_label(screen, sx, sy)

                if (tile.tile_type == TileType.FACILITY
                        and tile.facility_ref is not None
                        and tile.x == tile.facility_ref.x
                        and tile.y == tile.facility_ref.y):
                    self._draw_facility_label(screen, sx, sy, tile)

                if hover_tile == (x, y):
                    pygame.draw.rect(
                        screen, (255, 200, 80),
                        (sx + 1, sy + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2,
                    )

        self._draw_vehicles(screen, camera, vehicles)

    def _draw_rocks(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Draw rock-outcrop detail overlay on rocky tiles."""
        import random
        rng = random.Random(x * 100 + y)
        for _ in range(2):
            rx = x + rng.randint(4, TILE_SIZE - 5)
            ry = y + rng.randint(4, TILE_SIZE - 5)
            rw = rng.randint(5, 10)
            rh = rng.randint(3, 6)
            pygame.draw.ellipse(screen, (155, 85, 50), (rx - rw//2, ry - rh//2, rw, rh))
            pygame.draw.ellipse(screen, (195, 115, 68), (rx - rw//2, ry - rh//2, rw, rh), 1)

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

    def _draw_stop_marker(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Draw a small stop sign on stop tiles."""
        pygame.draw.rect(screen, (220, 220, 220), (x + TILE_SIZE // 2 - 1, y + 4, 2, 20))
        pygame.draw.rect(screen, (20, 100, 220), (x + TILE_SIZE // 2 - 6, y + 4, 12, 9))
        pygame.draw.rect(screen, (255, 255, 255), (x + TILE_SIZE // 2 - 6, y + 4, 12, 9), 1)
        font = self._get_stop_font()
        surf = font.render("S", True, (255, 255, 255))
        screen.blit(surf, (x + TILE_SIZE // 2 - surf.get_width() // 2, y + 4))

    def _draw_garage_label(self, screen: pygame.Surface, x: int, y: int) -> None:
        font = self._get_bank_font()
        surf = font.render("G", True, (255, 180, 80))
        screen.blit(surf, (
            x + TILE_SIZE // 2 - surf.get_width()  // 2,
            y + TILE_SIZE // 2 - surf.get_height() // 2,
        ))

    def _draw_facility_label(self, screen: pygame.Surface, sx: int, sy: int, tile) -> None:
        """Draw abbreviated facility name badge on the top-left tile of the facility."""
        name = tile.facility_ref.name
        abbr = _FAC_ABBR.get(name, name[:4].upper())

        badge = pygame.Surface((TILE_SIZE - 2, 12), pygame.SRCALPHA)
        badge.fill((0, 0, 0, 160))
        screen.blit(badge, (sx + 1, sy + TILE_SIZE - 13))
        font = self._get_label_font()
        surf = font.render(abbr, True, (255, 240, 180))
        screen.blit(surf, (
            sx + TILE_SIZE // 2 - surf.get_width() // 2,
            sy + TILE_SIZE - 13,
        ))

    def _draw_vehicles(self, screen: pygame.Surface, camera, vehicles) -> None:
        sp = self._get_sprites()
        for vehicle in vehicles:
            world_x = int(vehicle.x * TILE_SIZE + TILE_SIZE // 2)
            world_y = int(vehicle.y * TILE_SIZE + TILE_SIZE // 2)
            sx = world_x - camera.x
            sy = world_y - camera.y

            vsurf = sp.vehicle(vehicle.vdef_name, vehicle.color)
            vw, vh = vsurf.get_size()
            screen.blit(vsurf, (sx - vw // 2, sy - vh // 2))
