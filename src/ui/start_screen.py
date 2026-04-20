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
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_header = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 20)
        self.bg_color = (30, 30, 30)
        self.text_color = (220, 220, 220)

    def draw(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(self.bg_color)

        # Draw title
        title_surf = self.font_title.render("MARS AUTHORITY", True, self.text_color)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 60))
        surface.blit(title_surf, title_rect)

        # Draw controls
        y_offset = 120
        for i, (key, desc, is_header) in enumerate(_CONTROLS):
            font = self.font_header if is_header else self.font_text
            text_surf = font.render(f"{key:15} {desc}", True, self.text_color)
            text_rect = text_surf.get_rect(topleft=(50, y_offset + i * 30))
            surface.blit(text_surf, text_rect)

        return surface
