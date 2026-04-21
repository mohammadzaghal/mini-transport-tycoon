from __future__ import annotations

import math
import pygame

from src.config import WINDOW_WIDTH, WINDOW_HEIGHT
from src.ui.fonts import font_display, font_ui


_TIP_CARDS: list[tuple[str, str, str]] = [
    ("▶", "Roads & Tracks",   "Link mines · domes · colonies with [R] and [T]"),
    ("◆", "Stops & Routes",   "Place [S] stops, build routes, deploy vehicles"),
    ("◎", "Aquatics Unlock",  "First AQUATICS delivery to a city enables growth"),
    ("⬡", "Bridge Ore Cost",  "Bridges [K] spend Fe / Al / Ti — check HUD reserves"),
    ("⚙", "Garages & Fuel",   "[G] garages hold fuel for vehicle upgrades"),
    ("✦", "Controls & Speed", "[1]–[4] speed · [M] map · WASD pan · [F11] fullscreen"),
]

_CARD_BORDERS = [
    (200, 100, 50),
    (160,  90, 60),
    (180, 110, 45),
    (140,  80, 55),
    (190,  95, 40),
    (155,  85, 65),
]

_QUICK_TIPS: list[str] = [
    "Link mines & domes to colonies with [R] roads and [T] tracks.",
    "Place [S] stops, use the toolbar for routes & vehicles, then deploy.",
    "Cargo pays cash. First AQUATICS delivery to a city unlocks growth there.",
    "Bridges [K] spend ore (Fe / Al / Ti), not money — check the HUD.",
    "Garages [G] hold fuel for upgrades; [B] bulldoze, [Esc] cancels tools.",
    "[1]–[4] time speed · [M] minimap · [F11] fullscreen · WASD / arrows pan.",
]

_HELP_ROWS: list[tuple[str, str, bool]] = [
    ("FULL REFERENCE", "", True),
    ("", "", False),
    ("BUILDING & TOOLS", "", True),
    ("[R]", "Road ($100/tile) — connect the map", False),
    ("[T]", "Track ($150/tile) — Maglev routes", False),
    ("[B]", "Bulldoze — route first, then tile", False),
    ("[S]", "Stop — on road or track", False),
    ("[G]", "Garage ($2000) — upgrades & fuel deposit", False),
    ("[K]", "Bridge — click water; costs ore", False),
    ("[ESC]", "Cancel tool / close panels", False),
    ("", "", False),
    ("BRIDGES (ore, not $)", "", True),
    ("L1", "10 Iron — Hauler only", False),
    ("L2", "10 Alloy — Hauler + Rover", False),
    ("L3", "10 Titanium — all vehicles", False),
    ("", "", False),
    ("VEHICLES", "", True),
    ("Rover", "$1 200 · road · passengers", False),
    ("Hauler", "$800 · road · cargo", False),
    ("Maglev", "$2 500 · rail · bulk cargo", False),
    ("", "Road routes: Rover & Hauler. Rail: Maglev only.", False),
    ("", "", False),
    ("CITY UNLOCK (H₂O)", "", True),
    ("", "Until AQUATICS reaches a city, that city earns no delivery income.", False),
    ("", "After unlock: revenue + colony growth from deliveries.", False),
    ("", "", False),
    ("ORE & MINES", "", True),
    ("", "Mines produce Fe / Al / Ti — deliveries fill HUD reserves for bridges.", False),
    ("", "", False),
    ("FUEL & UPGRADES", "", True),
    ("", "Pick up FUEL at Fuel Rig; deposit at a stop next to a garage.", False),
    ("", "Open garage tile → spend fuel for level 2 / 3 stats.", False),
    ("", "", False),
    ("NAVIGATION", "", True),
    ("WASD / arrows", "Pan (when no tool locks keys)", False),
    ("Drag", "Pan map with mouse", False),
    ("Wheel", "Scroll map (Shift = horizontal)", False),
    ("", "", False),
    ("TIME", "", True),
    ("[1]", "Pause", False),
    ("[2]", "1×", False),
    ("[3]", "2×", False),
    ("[4]", "4×", False),
    ("", "", False),
    ("BULLDOZE", "", True),
    ("", "First click on route road clears route; second removes tile.", False),
    ("", "Colony roads protected. Bulldozed bridges become water.", False),
    ("", "", False),
    ("GROWTH", "", True),
    ("", "Deliver to unlocked cities for growth points → colony expands.", False),
]


class StartScreen:
    def __init__(self) -> None:
        self._btn_start: pygame.Rect | None = None
        self._btn_help: pygame.Rect | None = None
        self._btn_close: pygame.Rect | None = None
        self._help_open: bool = False
        self._help_scroll: int = 0
        self._help_max_scroll: int = 0
        self._pulse: float = 0.0

    def _text(
        self,
        surf: pygame.Surface,
        text: str,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int],
        bold: bool = False,
        anchor: str = "nw",
        *,
        display: bool = False,
    ) -> pygame.Rect:
        face = font_display(size, bold=bold) if display else font_ui(size, bold=bold)
        img = face.render(text, True, color)
        rx, ry = x, y
        if anchor == "center":
            rx -= img.get_width() // 2
            ry -= img.get_height() // 2
        elif anchor in ("ne", "e"):
            rx -= img.get_width()
        surf.blit(img, (rx, ry))
        return img.get_rect(topleft=(rx, ry))

    def _draw_background(self, screen: pygame.Surface) -> None:
        h = WINDOW_HEIGHT

        stops = [
            (0,   (8,   6,  18)),
            (280, (16,  10, 28)),
            (440, (38,  18, 12)),
            (700, (55,  26, 10)),
        ]
        for y in range(h):
            for i in range(len(stops) - 1):
                y0, c0 = stops[i]
                y1, c1 = stops[i + 1]
                if y0 <= y <= y1:
                    t = (y - y0) / (y1 - y0)
                    r = int(c0[0] + t * (c1[0] - c0[0]))
                    g = int(c0[1] + t * (c1[1] - c0[1]))
                    b = int(c0[2] + t * (c1[2] - c0[2]))
                    break
            pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        glow_layers = [
            (255, 130, 50, 55,  1280, 100,  0),
            (220,  90, 30, 38,  1480, 160, 22),
            (180,  60, 20, 24,  1680, 230, 44),
            (255, 160, 60, 14,  1900, 310, 66),
        ]
        base_y = int(h * 0.56)
        for lr, lg, lb, la, el_w, el_h, y_off in glow_layers:
            ex = (WINDOW_WIDTH - el_w) // 2
            ey = base_y + y_off
            glow = pygame.Surface((el_w, el_h), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (lr, lg, lb, la), glow.get_rect())
            screen.blit(glow, (ex, ey))

        for i in range(60):
            sx = (i * 97 + 13) % WINDOW_WIDTH
            sy = (i * 53 + 29) % int(h * 0.50)
            br = 160 + (i * 23) % 95

            if i % 7 == 0:
                col = (br, int(br * 0.85), int(br * 0.65))
            elif i % 5 == 0:
                col = (int(br * 0.75), int(br * 0.80), br)
            else:
                col = (br, br, int(br * 0.95))

            if i % 3 == 0:
                pygame.draw.circle(screen, col, (sx, sy), 1)
            else:
                screen.set_at((sx, sy), col)

            if i % 10 == 0:
                dim = (col[0] // 3, col[1] // 3, col[2] // 3)
                pygame.draw.line(screen, dim, (sx - 3, sy), (sx + 3, sy))
                pygame.draw.line(screen, dim, (sx, sy - 3), (sx, sy + 3))

        terrain_y_base = int(h * 0.60)
        prev = (0, terrain_y_base)
        for x in range(0, WINDOW_WIDTH, 4):
            y_off = (
                int(12 * math.sin(x * 0.008))
                + int(5 * math.sin(x * 0.021 + 1.3))
                + int(3 * math.sin(x * 0.047 + 2.7))
            )
            ty = terrain_y_base + y_off
            pygame.draw.line(screen, (60, 28, 14), prev, (x, ty), 2)
            prev = (x, ty)

        v = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for cx, cy in ((0, 0), (WINDOW_WIDTH, 0), (0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT)):
            pygame.draw.circle(v, (0, 0, 0, 130), (cx, cy), 340)
        screen.blit(v, (0, 0))