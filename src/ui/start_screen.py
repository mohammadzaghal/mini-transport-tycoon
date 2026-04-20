import pygame
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

_CONTROLS = [                                                    # v1.1 #18
    ("HOW TO PLAY (Mars Authority Edition)", "", True),
    ("", "", False),
    ("BUILDING & TOOLS", "", True),
    ("[R]",   "Dust Road ($100) — connect colonies", False),
    ("[T]",   "Mag-Rail ($150) — for Maglev trains", False),
    ("[B]",   "Bulldoze — remove roads/rails/bridges", False),
    ("[S]",   "Stop — place on road or rail near facility/colony", False),
    ("[G]",   "Garage ($2000) — vehicle maintenance & upgrades", False),
    ("[K]",   "Bridge — cross ice channels (costs ore, not money!)", False),
    ("[ESC]", "Cancel current action", False),
    ("", "", False),
    ("BRIDGES — costs ORE, not money", "", True),
    ("L1 Basic",  "10 Iron Ore (Fe) — Hauler only", False),
    ("L2 Reinf.", "10 Alloy Ore (Al) — Hauler + Rover", False),
    ("L3 Mag",    "10 Titanium Ore (Ti) — All vehicles incl. Maglev", False),
    ("",  "Mine ore → deliver to colony → check Fe/Al/Ti counters", False),
    ("", "", False),
    ("VEHICLES", "", True),
    ("ROVER",  "$1 200 · Road only · Passengers", False),
    ("HAULER", "$800 · Road only · Cargo", False),
    ("MAGLEV", "$2 500 · Rail only · Heavy cargo", False),
    ("",  "Road routes: Rover & Hauler only", False),
    ("",  "Rail routes: Maglev only", False),
    ("",  "Click ROUTE btn to list / remove routes", False),
    ("", "", False),
    ("CITY UNLOCK — H2O required!", "", True),
    ("",  "Cities earn NO income until water is connected", False),
    ("",  "Build road to nearest Aqua Dome (marked H2O)", False),
    ("",  "Deliver AQUATICS to city stop → city UNLOCKED", False),
    ("",  "After unlock: all cargo earns money + growth", False),
    ("", "", False),
    ("ORE MINE → 3 cargo types", "", True),
    ("",  "Each mine produces: Iron Ore + Alloy Ore + Titanium Ore", False),
    ("",  "Deliver to colony → earn money AND fill ore reserves", False),
    ("",  "Ore reserves (Fe/Al/Ti) shown top-right of HUD", False),
    ("",  "Spend ore reserves to build bridges — no money needed", False),
    ("", "", False),
    ("FUEL CHAIN (vehicle upgrades)", "", True),
    ("", "1. Route vehicle to Fuel Rig → pick up FUEL cargo", False),
    ("", "2. Drive to a stop ADJACENT to a Garage (not a colony)", False),
    ("", "3. FUEL auto-deposits to your FUEL reserve (top-right)", False),
    ("", "4. Click Garage tile → open upgrade panel", False),
    ("", "5. Spend FUEL: L2 = faster+more capacity, L3 = elite", False),
    ("", "", False),
    ("NAVIGATION", "", True),
    ("WASD / Arrows", "Scroll map", False),
    ("Mouse Drag",    "Pan the map", False),
    ("Mouse Wheel",   "Scroll (Shift = horizontal)", False),
    ("[M]",           "Toggle minimap (click to jump)", False),
    ("[F11]",         "Toggle fullscreen", False),
    ("", "", False),
    ("SPEED", "", True),
    ("[1]", "Pause", False),
    ("[2]", "Normal speed (1×)", False),
    ("[3]", "Fast speed (2×)", False),
    ("[4]", "Very fast speed (4×)", False),
    ("", "", False),
    ("BULLDOZE RULES", "", True),
    ("", "1st click on route road → removes route, road stays", False),
    ("", "2nd click on road → removes the road tile", False),
    ("", "City-colony roads cannot be bulldozed", False),
    ("", "Bridges revert to ice channel when bulldozed", False),
    ("", "", False),
    ("COLONY GROWTH", "", True),
    ("", "Deliver cargo to unlocked colony to earn growth points", False),
    ("", "When threshold reached: colony expands one ring outward", False),
    ("", "Internal colony roads extend automatically", False),
]

_MID = len(_CONTROLS) // 2


class StartScreen:
    def __init__(self) -> None:
        self._fonts: dict = {}
        self._btn_rect: tuple | None = None
        self._scroll_y: int = 0
        self._max_scroll: int = 0
        self._hint_tick: int = 0

    def _font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont("segoeui", size, bold=bold)
        return self._fonts[key]

    def _text(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        size: int,
        color: tuple,
        bold: bool = False,
        anchor: str = "nw",
    ) -> None:
        surf = self._font(size, bold).render(text, True, color)
        rx, ry = x, y
        if anchor == "center":
            rx -= surf.get_width() // 2
            ry -= surf.get_height() // 2
        elif anchor in ("ne", "e"):
            rx -= surf.get_width()
        screen.blit(surf, (rx, ry))


  def draw(self, screen: pygame.Surface) -> None:
        self._hint_tick += 1

       
        screen.fill((8, 5, 3))

        # Subtle dust-storm grid lines
        for i in range(0, WINDOW_WIDTH, 80):
            pygame.draw.line(screen, (18, 10, 6), (i, 0), (i, WINDOW_HEIGHT), 1)
        for j in range(0, WINDOW_HEIGHT, 80):
            pygame.draw.line(screen, (18, 10, 6), (0, j), (WINDOW_WIDTH, j), 1)

        
        title_panel_h = 170
        pygame.draw.rect(screen, (14, 8, 5), (0, 0, WINDOW_WIDTH, title_panel_h))
        pygame.draw.line(screen, (180, 90, 30), (0, title_panel_h), (WINDOW_WIDTH, title_panel_h), 3)


        cx = WINDOW_WIDTH // 2
        self._text(screen, "MINI TRANSPORT TYCOON", cx + 2, 20 + 2, 46,
                   (0, 0, 0), bold=True, anchor="center")
        self._text(screen, "MINI TRANSPORT TYCOON", cx, 20, 46,
                   (255, 180, 60), bold=True, anchor="center")
        self._text(screen, "MARS AUTHORITY", cx + 1, 72 + 1, 28,
                   (0, 0, 0), bold=True, anchor="center")
        self._text(screen, "MARS AUTHORITY", cx, 72, 28,
                   (220, 120, 50), bold=True, anchor="center")

    
        self._text(
            screen,
            "Build dust roads & mag-rails  ·  Connect colonies  ·  Transport resources  ·  Grow Mars",  # v1.1 #18
            cx, 110, 13, (180, 130, 80), anchor="center",
        )

        self._text(screen, "Prototype v1.2  |  Mars Authority Edition", cx, 133, 10,
                   (100, 70, 40), anchor="center")


        btn_w, btn_h = 300, 64
        bx = cx - btn_w // 2
        by = title_panel_h + 18
        self._btn_rect = (bx, by, bx + btn_w, by + btn_h)

        pygame.draw.rect(screen, (120, 60, 20), (bx - 3, by - 3, btn_w + 6, btn_h + 6), border_radius=12)
        pygame.draw.rect(screen, (60, 30, 10), (bx, by, btn_w, btn_h), border_radius=10)
        pygame.draw.rect(screen, (220, 140, 60), (bx, by, btn_w, btn_h), 3, border_radius=10)

        self._text(screen, "▶  LAUNCH MISSION", cx, by + btn_h // 2, 22,
                   (255, 220, 140), bold=True, anchor="center")
        self._text(screen, "or press  ENTER", cx, by + btn_h + 8, 10,
                   (140, 90, 50), anchor="center")

        
        ctrl_y_start = by + btn_h + 30
        ctrl_area_h = WINDOW_HEIGHT - ctrl_y_start - 14
        ctrl_surface = pygame.Surface((WINDOW_WIDTH, ctrl_area_h))
        ctrl_surface.fill((8, 5, 3))

        self._render_controls(ctrl_surface)

        screen.blit(ctrl_surface, (0, ctrl_y_start))


        if self._max_scroll > 0:
            hint_str = ("▼  Scroll for more" if (self._hint_tick // 30) % 2 == 0 else "▼")
            self._text(screen, hint_str,
                       WINDOW_WIDTH - 14, WINDOW_HEIGHT - 22, 12,
                       (255, 180, 60), bold=True, anchor="ne")