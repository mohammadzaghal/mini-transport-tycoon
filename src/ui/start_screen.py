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
    """Animated main menu displayed before the game starts.

    Shows the game title, a pulsing start button, and a scrollable "How to Play"
    help overlay.  Returns control to the game runner when the player clicks
    Start or presses Enter.
    """

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
        """Dramatic Mars gradient + horizon glow + stars + terrain ridge."""
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
                col = (br, int(br * 0.85), int(br * 0.65))   # warm yellow-white
            elif i % 5 == 0:
                col = (int(br * 0.75), int(br * 0.80), br)   # cold blue-white
            else:
                col = (br, br, int(br * 0.95))               # near-white

            if i % 3 == 0:
                pygame.draw.circle(screen, col, (sx, sy), 1)  # 2px dot
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

    def _draw_glass_card(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        border: tuple[int, int, int] = (200, 120, 70),
    ) -> None:
        inner = rect.inflate(-2, -2)
        card = pygame.Surface(inner.size, pygame.SRCALPHA)
        card.fill((18, 12, 10, 210))
        screen.blit(card, inner.topleft)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=16)
        pygame.draw.rect(screen, (40, 24, 16), rect, width=1, border_radius=16)

    def _draw_button(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        *,
        primary: bool,
        hover: bool,
    ) -> None:
        if primary:

            glow_alpha = int(55 + 35 * math.sin(self._pulse))
            glow_rect = rect.inflate(14, 14)
            glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf, (255, 160, 60, glow_alpha),
                glow_surf.get_rect(), border_radius=18,
            )
            screen.blit(glow_surf, glow_rect.topleft)

            pygame.draw.rect(screen, (180, 90, 30), rect.inflate(4, 4),
                             width=1, border_radius=14)

            fill = (200, 95, 35) if hover else (150, 70, 28)
            edge = (255, 190, 110) if hover else (230, 150, 80)
            text_col = (255, 200, 120)

            pygame.draw.rect(screen, fill, rect, border_radius=12)
            pygame.draw.rect(screen, edge, rect, width=2, border_radius=12)
            self._text(screen, label, rect.centerx, rect.centery, 20,
                       text_col, bold=True, anchor="center")

        else:

            ghost_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            ghost_fill = (45, 28, 18, 160) if hover else (28, 18, 12, 120)
            ghost_surf.fill(ghost_fill)
            screen.blit(ghost_surf, rect.topleft)

            border_width = 2 if hover else 1
            border_col = (160, 110, 75) if hover else (100, 70, 50)
            text_col = (220, 190, 160) if hover else (160, 130, 100)
            pygame.draw.rect(screen, border_col, rect, width=border_width, border_radius=12)
            self._text(screen, label, rect.centerx, rect.centery, 17,
                       text_col, bold=True, anchor="center")

    def draw(self, screen: pygame.Surface) -> None:
        """Render the start screen (title, buttons, optional help overlay) to the screen.

        Args:
            screen: The pygame display surface.
        """
        self._pulse += 0.04
        mx, my = pygame.mouse.get_pos()

        self._draw_background(screen)

        cx = WINDOW_WIDTH // 2
        title_y = 48

        shadow_stack = [
            (6, 6, (12,   6,   3)),
            (4, 4, (45,  18,   6)),
            (2, 2, (120,  50,  15)),
            (1, 1, (200, 110,  40)),
        ]
        for ox, oy, sc in shadow_stack:
            self._text(screen, "MINI TRANSPORT TYCOON", cx + ox, title_y + oy, 56,
                       sc, bold=True, anchor="center", display=True)
        self._text(screen, "MINI TRANSPORT TYCOON", cx, title_y, 56,
                   (255, 215, 145), bold=True, anchor="center", display=True)

        badge_w, badge_h = 272, 30
        badge_x = cx - badge_w // 2
        badge_y = title_y + 60
        badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        badge_surf.fill((80, 35, 12, 185))
        screen.blit(badge_surf, (badge_x, badge_y))
        pygame.draw.rect(screen, (220, 110, 50),
                         pygame.Rect(badge_x, badge_y, badge_w, badge_h),
                         width=1, border_radius=10)

        pygame.draw.line(screen, (255, 160, 70),
                         (badge_x + 6, badge_y + 1), (badge_x + badge_w - 6, badge_y + 1))

        sub_glow = int(200 + 40 * math.sin(self._pulse))
        self._text(screen, "MARS COLONY EDITION", cx, badge_y + badge_h // 2, 15,
                   (sub_glow, 150, 80), bold=True, anchor="center", display=True)

        self._text(screen, "Roads · rails · cargo · growth",
                   cx, title_y + 100, 15, (200, 170, 140), anchor="center")
        self._text(screen, "Prototype — each new game uses a fresh procedural map",
                   cx, title_y + 120, 11, (120, 95, 80), anchor="center")

        div_y = title_y + 138
        pygame.draw.line(screen, (90, 55, 35), (470, div_y), (612, div_y))
        pygame.draw.line(screen, (90, 55, 35), (668, div_y), (810, div_y))
        pygame.draw.circle(screen, (200, 120, 60), (640, div_y), 3)
        pygame.draw.circle(screen, (90, 55, 35), (640, div_y), 5, width=1)

        gap = 18
        bw_p, bh = 280, 50
        bw_s = 220
        total_w = bw_p + gap + bw_s
        bx0 = cx - total_w // 2
        by_btn = title_y + 158

        self._btn_start = pygame.Rect(bx0, by_btn, bw_p, bh)
        self._btn_help = pygame.Rect(bx0 + bw_p + gap, by_btn, bw_s, bh)

        h_start = self._btn_start.collidepoint(mx, my)
        h_help = self._btn_help.collidepoint(mx, my) and not self._help_open
        self._draw_button(screen, self._btn_start, "▶  Start game", primary=True, hover=h_start)
        self._draw_button(screen, self._btn_help, "How to play", primary=False, hover=h_help)

        self._text(screen, "or press  Enter", cx, by_btn + bh + 8, 11,
                   (140, 110, 90), anchor="center")

        header_y = by_btn + bh + 32
        self._text(screen, "BEFORE YOU LAUNCH", 80, header_y, 11,
                   (200, 110, 55), bold=True)
        pygame.draw.line(screen, (80, 42, 22),
                         (258, header_y + 7), (WINDOW_WIDTH - 80, header_y + 7))

        card_w, card_h = 364, 82
        col_gap, row_gap = 14, 12
        col_xs = [80, 80 + card_w + col_gap, 80 + 2 * (card_w + col_gap)]
        row_ys = [header_y + 22, header_y + 22 + card_h + row_gap]

        for idx, (icon, phrase, detail) in enumerate(_TIP_CARDS):
            col = idx % 3
            row = idx // 3
            cx_card = col_xs[col]
            cy_card = row_ys[row]
            border_col = _CARD_BORDERS[idx]
            card_rect = pygame.Rect(cx_card, cy_card, card_w, card_h)

            inner = card_rect.inflate(-2, -2)
            fill_surf = pygame.Surface(inner.size, pygame.SRCALPHA)
            fill_surf.fill((18, 10, 6, 200))
            screen.blit(fill_surf, inner.topleft)

            pygame.draw.rect(screen, border_col, card_rect, width=1, border_radius=10)
            hl = (border_col[0] // 4, border_col[1] // 4, border_col[2] // 4)
            pygame.draw.line(screen, hl,
                             (cx_card + 6, cy_card + 1), (cx_card + card_w - 6, cy_card + 1))

            self._text(screen, icon, cx_card + 14, cy_card + 16, 22, (220, 140, 60))

            self._text(screen, phrase, cx_card + 46, cy_card + 12, 13,
                       (255, 200, 130), bold=True)

            self._text(screen, detail, cx_card + 46, cy_card + 32, 11, (185, 158, 130))

            pygame.draw.line(screen, border_col,
                             (cx_card + 14, cy_card + card_h - 9),
                             (cx_card + 52, cy_card + card_h - 9))

        grid_bottom = row_ys[1] + card_h
        strip_y = grid_bottom + 18
        pygame.draw.line(screen, (55, 32, 18), (80, strip_y), (WINDOW_WIDTH - 80, strip_y))
        shortcut_items = [
            "[R] Road", "[T] Track", "[S] Stop", "[K] Bridge",
            "[G] Garage", "[B] Demo", "[M] Minimap", "[1–4] Speed",
        ]
        item_w = (WINDOW_WIDTH - 160) // len(shortcut_items)
        for i, label in enumerate(shortcut_items):
            ix = 80 + i * item_w + item_w // 2
            self._text(screen, label, ix, strip_y + 7, 10, (130, 95, 68), anchor="center")
        pygame.draw.line(screen, (55, 32, 18),
                         (80, strip_y + 26), (WINDOW_WIDTH - 80, strip_y + 26))

        sep_y = WINDOW_HEIGHT - 44
        pygame.draw.line(screen, (65, 38, 22), (80, sep_y), (WINDOW_WIDTH - 80, sep_y))
        pygame.draw.rect(screen, (65, 38, 22), pygame.Rect(636, sep_y - 2, 8, 4))
        self._text(
            screen,
            "Tip: use the toolbar for routes, vehicles, and bridge levels — keys are shortcuts.",
            cx, WINDOW_HEIGHT - 22, 11,
            (155, 128, 100), anchor="center",
        )

        if self._help_open:
            self._draw_help_overlay(screen, mx, my)

    def _draw_help_overlay(self, screen: pygame.Surface, mx: int, my: int) -> None:
        veil = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 200))
        screen.blit(veil, (0, 0))

        panel_w, panel_h = 720, 520
        px = (WINDOW_WIDTH - panel_w) // 2
        py = (WINDOW_HEIGHT - panel_h) // 2
        panel = pygame.Rect(px, py, panel_w, panel_h)

        inner = panel.inflate(-4, -4)
        body = pygame.Surface(inner.size, pygame.SRCALPHA)
        body.fill((14, 10, 8, 245))
        screen.blit(body, inner.topleft)
        pygame.draw.rect(screen, (210, 130, 70), panel, width=2, border_radius=18)

        title_y = panel.y + 22
        self._text(screen, "How to play", panel.centerx, title_y, 24,
                   (255, 200, 130), bold=True, anchor="center", display=True)
        self._text(screen, "Full controls & systems", panel.centerx, title_y + 30, 12,
                   (160, 130, 110), anchor="center")

        clip = pygame.Rect(panel.x + 20, panel.y + 64, panel_w - 40, panel_h - 120)
        clip_surf = screen.subsurface(clip)
        col_w = clip.width // 2 - 12
        x0 = 0
        x1 = col_w + 24
        mid = len(_HELP_ROWS) // 2
        y_base = 8 - self._help_scroll

        y_left = y_base
        y_right = y_base
        max_y = y_base

        for idx, (key_label, desc, is_header) in enumerate(_HELP_ROWS):
            in_right = idx >= mid
            cx = x1 if in_right else x0
            cy = y_right if in_right else y_left
            row_h = 24 if is_header else (10 if key_label == "" else 19)

            if -row_h <= cy <= clip.height + row_h:
                if is_header:
                    self._text(clip_surf, key_label, cx, cy, 12, (240, 160, 80), bold=True)
                    pygame.draw.line(
                        clip_surf, (120, 70, 40),
                        (cx, cy + 16), (cx + col_w - 8, cy + 16), 1,
                    )
                elif key_label == "":
                    pass
                else:
                    if key_label:
                        badge_w = max(52, len(key_label) * 7 + 12)
                        pygame.draw.rect(clip_surf, (36, 22, 14), (cx, cy + 1, badge_w, 16), border_radius=4)
                        pygame.draw.rect(clip_surf, (95, 55, 30), (cx, cy + 1, badge_w, 16), 1, border_radius=4)
                        self._text(
                            clip_surf, key_label, cx + badge_w // 2, cy + 9, 10,
                            (255, 210, 140), bold=True, anchor="center",
                        )
                        if desc:
                            self._text(clip_surf, desc, cx + badge_w + 8, cy + 2, 10, (190, 165, 135))
                    else:
                        self._text(clip_surf, "·  " + desc, cx + 6, cy + 2, 10, (165, 140, 115))

            if in_right:
                y_right += row_h
            else:
                y_left += row_h
            max_y = max(max_y, y_left, y_right)

        total_content = max_y - y_base + self._help_scroll + 24
        self._help_max_scroll = max(0, total_content - clip.height)

        close_w, close_h = 120, 40
        self._btn_close = pygame.Rect(
            panel.right - close_w - 18, panel.bottom - close_h - 16, close_w, close_h,
        )
        h_close = self._btn_close.collidepoint(mx, my)
        self._draw_button(screen, self._btn_close, "Close", primary=False, hover=h_close)

        if self._help_max_scroll > 0:
            self._text(
                screen, "Scroll  ·  Esc to close", panel.x + 24, panel.bottom - 36, 11,
                (130, 110, 95),
            )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the player wants to start the game."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._help_open:
                    self._help_open = False
                    self._help_scroll = 0
                return False
            if event.key == pygame.K_RETURN and not self._help_open:
                return True

        if event.type == pygame.MOUSEWHEEL and self._help_open:
            self._help_scroll = max(
                0, min(self._help_max_scroll, self._help_scroll - event.y * 28),
            )
            return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            if self._help_open:
                if self._btn_close and self._btn_close.collidepoint(x, y):
                    self._help_open = False
                    self._help_scroll = 0
                    return False

                panel_w, panel_h = 720, 520
                px = (WINDOW_WIDTH - panel_w) // 2
                py = (WINDOW_HEIGHT - panel_h) // 2
                panel = pygame.Rect(px, py, panel_w, panel_h)
                if not panel.collidepoint(x, y):
                    self._help_open = False
                    self._help_scroll = 0
                    return False
                return False

            if self._btn_start and self._btn_start.collidepoint(x, y):
                return True
            if self._btn_help and self._btn_help.collidepoint(x, y):
                self._help_open = True
                self._help_scroll = 0

        return False
