from __future__ import annotations

import pygame
from src.enums import BridgeType, FacilityType, TileType

TILE = 32


_REGOLITH_BASE  = (185, 100, 55)
_REGOLITH_DARK  = (148,  74, 32)
_REGOLITH_LIGHT = (222, 135, 78)

_ROCK_DARK   = (110, 55, 30)
_ROCK_MID    = (155, 85, 50)
_ROCK_LIGHT  = (195, 115, 68)
_ROCK_ACCENT = (80,  40, 18)

_DUST_BASE = (155, 120, 80)
_DUST_DARK = (120,  90, 55)
_DUST_MARK = (215, 180, 120)

_TRACK_BALLAST = (100, 70, 50)                                
_TRACK_RAIL    = (190, 195, 200)                                
_TRACK_TIE     = (130, 95, 65)                                    

_ICE_DEEP  = (170, 195, 220)
_ICE_MID   = (195, 215, 232)
_ICE_LIGHT = (220, 235, 248)
_ICE_SHEEN = (245, 250, 255)

_DOME_HULL   = (170, 178, 195)
_DOME_ACC1   = ( 80, 160, 200)
_DOME_ACC2   = (100, 130, 165)
_DOME_ACC3   = ( 60, 100, 155)
_DOME_WINDOW = (100, 240, 255)

_FAC_COLORS = {
    FacilityType.ORE_MINE:    ((60,  50,  70), (130,  95, 150)),
    FacilityType.FUEL_RIG:    ((35,  35,  45), ( 65,  65,  75)),
    FacilityType.AQUA_DOME:   ((30,  80, 120), ( 60, 140, 200)),
    FacilityType.CRYSTAL_LAB: ((55,  85, 125), ( 95, 150, 210)),
}

_BRIDGE_COLORS = {
    BridgeType.WOODEN: ((130, 95, 55), (165, 125, 75)),
    BridgeType.STONE:  ((140, 130, 120), (170, 160, 150)),
    BridgeType.STEEL:  ((100, 125, 145), (150, 175, 195)),
}

ROUTE_ROAD_COLOR  = (220, 170,  60)
ENTRY_POINT_COLOR = (  0, 210, 200)


class SpriteCache:
    _instance: SpriteCache | None = None

    def __init__(self) -> None:
        self._cache: dict = {}
        self._built = False

    @classmethod
    def get(cls) -> SpriteCache:
        if cls._instance is None:
            cls._instance = SpriteCache()
        return cls._instance

    def build(self) -> None:
        if self._built:
            return
        self._cache["grass"]       = make_regolith_tile()
        self._cache["forest"]      = make_rock_tile()
        self._cache["water"]       = make_ice_tile()
        self._cache["road"]        = make_road_tile()
        self._cache["road_route"]  = make_road_tile(route=True)
        self._cache["road_entry"]  = make_entry_tile()
        self._cache["track"]       = make_track_tile()            
        self._cache["track_route"] = make_track_route_tile()     
        self._cache["city"]        = make_city_tile(0)
        self._cache["city_bank"]   = make_city_bank_tile()
        self._cache["garage"]      = make_garage_tile()
        for bt in BridgeType:
            self._cache[f"bridge_{bt.name}"]       = make_bridge_tile(bt)
            self._cache[f"bridge_{bt.name}_route"] = make_bridge_route_tile(bt)
        for ft in FacilityType:
            self._cache[f"fac_{ft.name}"] = make_facility_tile(ft)
        # Vehicles
        self._cache["rover"]  = make_bus_sprite((120, 200, 80))  
        self._cache["hauler"] = make_truck_sprite((80, 160, 220))
        self._cache["maglev"] = make_train_sprite((230, 140, 50))
        self._built = True

    def tile(self, key: str) -> pygame.Surface | None:
        return self._cache.get(key)

    def vehicle(self, vdef_name: str, color_hex: str) -> pygame.Surface:
        """Return the appropriate vehicle sprite tinted with the vehicle's colour."""
        key = f"v_{vdef_name}_{color_hex}"
        if key not in self._cache:
            rgb = _hex_to_rgb(color_hex)
            name = vdef_name.lower()
            if "maglev" in name or "train" in name:              
                base = make_train_sprite(rgb)
            elif "rover" in name or "bus" in name:
                base = make_bus_sprite(rgb)
            else:
                base = make_truck_sprite(rgb)
            self._cache[key] = base
        return self._cache[key]



def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _surf(w: int = TILE, h: int = TILE, alpha: bool = False) -> pygame.Surface:
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((w, h), flags)



def make_regolith_tile() -> pygame.Surface:
    """Rust-orange Martian regolith — replaces grass."""
    s = _surf()
    s.fill(_REGOLITH_BASE)
    import random
    rng = random.Random(42)
    for _ in range(16):
        dx = rng.randint(1, TILE - 2)
        dy = rng.randint(1, TILE - 2)
        c = _REGOLITH_DARK if rng.random() < 0.5 else _REGOLITH_LIGHT
        pygame.draw.circle(s, c, (dx, dy), 1)
    return s


def make_rock_tile() -> pygame.Surface:
    """Rocky outcrop — replaces forest."""
    s = _surf()
    s.fill(_ROCK_DARK)
    import random
    rng = random.Random(13)
    for _ in range(6):
        dx = rng.randint(3, TILE - 4)
        dy = rng.randint(3, TILE - 4)
        r = rng.randint(3, 6)
        pygame.draw.ellipse(s, _ROCK_MID, (dx - r, dy - r//2, r*2, r))
        pygame.draw.ellipse(s, _ROCK_LIGHT, (dx - r//2, dy - r//3, r, r//2))
    return s


def make_ice_tile() -> pygame.Surface:
    """Frozen ice channel — replaces water."""
    s = _surf()
    s.fill(_ICE_DEEP)
    for i in range(0, TILE, 6):
        pygame.draw.line(s, _ICE_MID, (0, i), (TILE, i + 2), 1)
    for px in range(3, TILE, 10):
        for py in range(5, TILE, 10):
            pygame.draw.circle(s, _ICE_SHEEN, (px, py), 1)
    return s


def make_road_tile(route: bool = False) -> pygame.Surface:
    """Compressed dust track."""
    s = _surf()
    base = ROUTE_ROAD_COLOR if route else _DUST_BASE
    s.fill(base)
    dark = tuple(max(0, c - 25) for c in base)
    pygame.draw.line(s, dark, (0, 0), (TILE - 1, 0), 2)
    pygame.draw.line(s, dark, (0, TILE - 1), (TILE - 1, TILE - 1), 2)
    pygame.draw.line(s, dark, (0, 0), (0, TILE - 1), 2)
    pygame.draw.line(s, dark, (TILE - 1, 0), (TILE - 1, TILE - 1), 2)
    mark = _DUST_MARK if not route else (255, 220, 100)
    for i in range(4, TILE - 4, 8):
        pygame.draw.line(s, mark, (i, TILE // 2), (i + 4, TILE // 2), 1)
        pygame.draw.line(s, mark, (TILE // 2, i), (TILE // 2, i + 4), 1)
    return s


def make_track_tile() -> pygame.Surface:                      
    """Mag-rail track: dark ballast with cross-ties and two rails."""
    s = _surf()
    s.fill(_TRACK_BALLAST)
    for i in range(2, TILE, 6):
        pygame.draw.line(s, _TRACK_TIE, (i, 8), (i, TILE - 9), 2)
        pygame.draw.line(s, _TRACK_TIE, (8, i), (TILE - 9, i), 2)
    pygame.draw.line(s, _TRACK_RAIL, (0, TILE // 2 - 4), (TILE, TILE // 2 - 4), 2)
    pygame.draw.line(s, _TRACK_RAIL, (0, TILE // 2 + 4), (TILE, TILE // 2 + 4), 2)
    pygame.draw.line(s, _TRACK_RAIL, (TILE // 2 - 4, 0), (TILE // 2 - 4, TILE), 2)
    pygame.draw.line(s, _TRACK_RAIL, (TILE // 2 + 4, 0), (TILE // 2 + 4, TILE), 2)
    return s


def make_track_route_tile() -> pygame.Surface:                   
    s = make_track_tile()
    amber = (255, 200, 80)
    pygame.draw.line(s, amber, (0, TILE // 2 - 4), (TILE, TILE // 2 - 4), 2)
    pygame.draw.line(s, amber, (0, TILE // 2 + 4), (TILE, TILE // 2 + 4), 2)
    pygame.draw.line(s, amber, (TILE // 2 - 4, 0), (TILE // 2 - 4, TILE), 2)
    pygame.draw.line(s, amber, (TILE // 2 + 4, 0), (TILE // 2 + 4, TILE), 2)
    return s


def make_entry_tile() -> pygame.Surface:
    s = _surf()
    s.fill(ENTRY_POINT_COLOR)
    return s


def make_city_tile(variant: int = 0) -> pygame.Surface:
    """Habitat dome tile."""
    s = _surf()
    s.fill(_DOME_HULL)
    acc_colors = [_DOME_ACC1, _DOME_ACC2, _DOME_ACC3]
    acc = acc_colors[variant % len(acc_colors)]
    pygame.draw.rect(s, acc, (3, 3, TILE - 6, TILE - 10))
    # Dome arc on top
    pygame.draw.arc(s, tuple(min(255, c + 40) for c in acc),
                    (4, 2, TILE - 8, 14), 0, 3.14159, 2)
    shadow = tuple(max(0, c - 40) for c in acc)
    pygame.draw.line(s, shadow, (TILE - 3, 3), (TILE - 3, TILE - 10), 3)
    pygame.draw.line(s, shadow, (3, TILE - 10), (TILE - 3, TILE - 10), 3)
    # Glow windows (cyan)
    for wx in range(6, TILE - 4, 8):
        for wy in range(6, TILE - 8, 8):
            pygame.draw.rect(s, _DOME_WINDOW, (wx, wy, 4, 4))
    return s


def make_city_bank_tile() -> pygame.Surface:
    s = make_city_tile(2)
    pygame.draw.rect(s, (220, 190, 80), (2, 2, TILE - 4, TILE - 4), 2)
    return s


def make_facility_tile(fac_type: FacilityType) -> pygame.Surface:
    s = _surf()
    floor_c, roof_c = _FAC_COLORS.get(fac_type, ((80, 80, 80), (120, 120, 120)))
    s.fill(floor_c)
    pygame.draw.rect(s, roof_c, (4, 4, TILE - 8, TILE - 8))

    cx, cy = TILE // 2, TILE // 2

    if fac_type == FacilityType.ORE_MINE:
        col = (255, 165, 40)
        pygame.draw.line(s, col, (cx - 8, cy - 8), (cx + 8, cy + 8), 3)
        pygame.draw.line(s, col, (cx + 8, cy - 8), (cx - 8, cy + 8), 3)
        pygame.draw.circle(s, (255, 220, 100), (cx - 8, cy - 8), 3)
        pygame.draw.circle(s, (255, 220, 100), (cx + 8, cy - 8), 3)

    elif fac_type == FacilityType.FUEL_RIG:
        col = (200, 200, 80)
        pts = [(cx, cy - 11), (cx - 7, cy + 7), (cx + 7, cy + 7)]
        pygame.draw.polygon(s, col, pts, 2)
        pygame.draw.line(s, col, (cx - 7, cy + 7), (cx + 7, cy + 7), 3)
        pygame.draw.line(s, col, (cx - 2, cy - 2), (cx + 2, cy - 2), 2)
        pygame.draw.line(s, (255, 200, 60), (cx, cy + 7), (cx, cy + 12), 2)

    elif fac_type == FacilityType.AQUA_DOME:
        col = (80, 200, 255)
        pygame.draw.circle(s, col, (cx, cy), 9, 2)
        for ry in [cy - 4, cy, cy + 4]:
            pygame.draw.line(s, col, (cx - 8, ry), (cx + 8, ry), 1)
        pygame.draw.circle(s, (150, 230, 255), (cx, cy - 2), 2)

    elif fac_type == FacilityType.CRYSTAL_LAB:
        col = (100, 220, 255)
        for ox in [-7, 0, 7]:
            h_shard = 10 if ox == 0 else 7
            pts = [(cx + ox, cy - h_shard), (cx + ox - 3, cy + 5), (cx + ox + 3, cy + 5)]
            pygame.draw.polygon(s, col, pts, 0)
            pygame.draw.polygon(s, (200, 245, 255), pts, 1)

    return s


def make_bridge_tile(bridge_type: BridgeType) -> pygame.Surface:
    s = make_ice_tile()
    deck_c, rail_c = _BRIDGE_COLORS.get(bridge_type, ((140, 130, 120), (170, 160, 150)))
    pygame.draw.rect(s, deck_c, (0, 10, TILE, 12))
    pygame.draw.rect(s, deck_c, (10, 0, 12, TILE))
    pygame.draw.line(s, rail_c, (0, 10), (TILE, 10), 2)
    pygame.draw.line(s, rail_c, (0, 22), (TILE, 22), 2)
    pygame.draw.line(s, rail_c, (10, 0), (10, TILE), 2)
    pygame.draw.line(s, rail_c, (22, 0), (22, TILE), 2)
    return s


def make_bridge_route_tile(bridge_type: BridgeType) -> pygame.Surface:
    s = make_bridge_tile(bridge_type)
    amber = (220, 170, 60)
    pygame.draw.line(s, amber, (4, 4), (TILE - 4, TILE - 4), 2)
    pygame.draw.line(s, amber, (TILE - 4, 4), (4, TILE - 4), 2)
    return s


def make_garage_tile() -> pygame.Surface:
    s = _surf()
    s.fill((70, 65, 75))
    pygame.draw.rect(s, (45, 42, 52), (4, 10, TILE - 8, TILE - 14))
    pygame.draw.rect(s, (100, 95, 110), (4, 10, TILE - 8, TILE - 14), 2)
    pygame.draw.line(s, (65, 62, 72), (16, 10), (16, TILE - 4), 1)
    pygame.draw.line(s, (65, 62, 72), (4, 16), (TILE - 4, 16), 1)
    pygame.draw.rect(s, (90, 85, 100), (2, 2, TILE - 4, 9))
    pygame.draw.rect(s, (200, 130, 50), (4, 10, TILE - 8, TILE - 14), 1)
    return s



def make_truck_sprite(color: tuple) -> pygame.Surface:
    w, h = 28, 14
    s = _surf(w, h, alpha=True)
    s.fill((0, 0, 0, 0))
    dark = tuple(max(0, c - 50) for c in color)
    light = tuple(min(255, c + 50) for c in color)
    pygame.draw.rect(s, dark,  (0, 1, 18, h - 2))
    pygame.draw.rect(s, color, (1, 2, 16, h - 4))
    pygame.draw.rect(s, dark,  (18, 2, 10, h - 4))
    pygame.draw.rect(s, light, (19, 3, 8, h - 6))
    pygame.draw.rect(s, (180, 220, 255), (21, 4, 5, 5))
    pygame.draw.rect(s, (20, 20, 20), (0, 1, 18, h - 2), 1)
    pygame.draw.rect(s, (20, 20, 20), (18, 2, 10, h - 4), 1)
    wc = (40, 40, 40)
    for wx, wy in [(2, 0), (2, h - 2), (16, 0), (16, h - 2)]:
        pygame.draw.circle(s, wc, (wx + 1, wy + 1), 2)
    return s


def make_bus_sprite(color: tuple) -> pygame.Surface:
    w, h = 28, 16
    s = _surf(w, h, alpha=True)
    s.fill((0, 0, 0, 0))
    dark = tuple(max(0, c - 40) for c in color)
    pygame.draw.rect(s, dark,  (0, 0, w, h))
    pygame.draw.rect(s, color, (1, 1, w - 2, h - 2))
    for wx in range(4, w - 8, 6):
        pygame.draw.rect(s, (220, 240, 255), (wx, 2, 4, 5))
        pygame.draw.rect(s, (220, 240, 255), (wx, h - 7, 4, 5))
    pygame.draw.rect(s, (220, 240, 255), (w - 8, 3, 6, h - 6))
    pygame.draw.rect(s, (20, 20, 20), (0, 0, w, h), 1)
    wc = (40, 40, 40)
    for wx2, wy2 in [(3, 0), (3, h - 1), (20, 0), (20, h - 1)]:
        pygame.draw.circle(s, wc, (wx2, wy2), 2)
    return s


def make_train_sprite(color: tuple) -> pygame.Surface:        
    w, h = 36, 16
    s = _surf(w, h, alpha=True)
    s.fill((0, 0, 0, 0))
    dark = tuple(max(0, c - 50) for c in color)
    light = tuple(min(255, c + 60) for c in color)
    pygame.draw.rect(s, dark,  (0, 1, 24, h - 2))
    pygame.draw.rect(s, color, (1, 2, 22, h - 4))
    pygame.draw.rect(s, dark,  (24, 1, 12, h - 2))
    pygame.draw.rect(s, light, (25, 2, 10, h - 4))
    pygame.draw.rect(s, (200, 230, 255), (27, 3, 4, 4))
    pygame.draw.rect(s, (200, 230, 255), (27, h - 7, 4, 4))
    pygame.draw.rect(s, dark, (34, 4, 2, h - 8))
    pygame.draw.rect(s, (20, 20, 20), (0, 1, 24, h - 2), 1)
    pygame.draw.rect(s, (20, 20, 20), (24, 1, 12, h - 2), 1)
    wc = (40, 40, 40)
    for wx in [2, 8, 14, 20, 27]:
        pygame.draw.circle(s, wc, (wx, 1), 2)
        pygame.draw.circle(s, wc, (wx, h - 2), 2)
    return s


def make_rover_sprite(color: tuple) -> pygame.Surface:
    w, h = 20, 12
    s = _surf(w, h, alpha=True)
    s.fill((0, 0, 0, 0))
    dark = tuple(max(0, c - 50) for c in color)
    pygame.draw.rect(s, dark,  (1, 1, w - 2, h - 2))
    pygame.draw.rect(s, color, (2, 2, w - 4, h - 4))
    pygame.draw.rect(s, (200, 230, 255), (w - 7, 3, 5, h - 6))
    pygame.draw.rect(s, (20, 20, 20), (1, 1, w - 2, h - 2), 1)
    wc = (40, 40, 40)
    for wx, wy in [(2, 0), (2, h - 1), (14, 0), (14, h - 1)]:
        pygame.draw.circle(s, wc, (wx, wy), 2)
    return s
