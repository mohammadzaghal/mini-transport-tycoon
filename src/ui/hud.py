from __future__ import annotations

from typing import Optional, List

import pygame

from src.config import BOTTOM_BAR_HEIGHT, VEHICLE_DEFS, VEHICLE_LEVEL_DEFS, WINDOW_HEIGHT, WINDOW_WIDTH
from src.enums import TimeSpeed, Tool, BridgeType, VehicleType


_BAR_Y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT

_BTN_Y1 = _BAR_Y + 12
_BTN_Y2 = _BAR_Y + 52

_BTN_ROAD      = (10,   _BTN_Y1, 90,   _BTN_Y2)
_BTN_TRACK     = (94,   _BTN_Y1, 184,  _BTN_Y2)                
_BTN_VEHICLES  = (188,  _BTN_Y1, 278,  _BTN_Y2)
_BTN_ROUTE     = (282,  _BTN_Y1, 362,  _BTN_Y2)
_BTN_STOP      = (366,  _BTN_Y1, 440,  _BTN_Y2)
_BTN_BRIDGE    = (444,  _BTN_Y1, 524,  _BTN_Y2)
_BTN_BULLDOZE  = (528,  _BTN_Y1, 624,  _BTN_Y2)
_BTN_GARAGE    = (628,  _BTN_Y1, 714,  _BTN_Y2)

_SPD_Y1 = _BAR_Y + 58
_SPD_Y2 = _BAR_Y + 88
_SPD_X  = WINDOW_WIDTH - 310
_BTN_SPD_PAUSE = (_SPD_X,       _SPD_Y1, _SPD_X + 38,  _SPD_Y2)
_BTN_SPD_1     = (_SPD_X + 42,  _SPD_Y1, _SPD_X + 80,  _SPD_Y2)
_BTN_SPD_2     = (_SPD_X + 84,  _SPD_Y1, _SPD_X + 122, _SPD_Y2)
_BTN_SPD_4     = (_SPD_X + 126, _SPD_Y1, _SPD_X + 164, _SPD_Y2)

_BRIDGE_BTN_Y1 = _BAR_Y - 50
_BRIDGE_BTN_Y2 = _BAR_Y - 8
_BTN_BRIDGE_L1 = (444, _BRIDGE_BTN_Y1, 524, _BRIDGE_BTN_Y2)
_BTN_BRIDGE_L2 = (528, _BRIDGE_BTN_Y1, 608, _BRIDGE_BTN_Y2)
_BTN_BRIDGE_L3 = (612, _BRIDGE_BTN_Y1, 692, _BRIDGE_BTN_Y2)

_POPUP_Y1 = _BAR_Y - 190
_POPUP_Y2 = _BAR_Y - 10
_POPUP_X1 = 10
_CARD_W   = 170
_CARD_GAP = 10
_FLEET_X1    = _POPUP_X1 + len(VEHICLE_DEFS) * (_CARD_W + _CARD_GAP) + 20
_FLEET_W     = 230
_FLEET_X2    = _FLEET_X1 + _FLEET_W
_FLEET_ROW_H = 22

_ROUTES_PANEL_X = 10                                            
_ROUTES_PANEL_Y = _BAR_Y - 220
_ROUTES_PANEL_W = 500
_ROUTES_ROW_H   = 24

_GARAGE_PANEL_X = WINDOW_WIDTH - 420                            
_GARAGE_PANEL_Y = _BAR_Y - 260
_GARAGE_PANEL_W = 410
_GARAGE_ROW_H   = 28



def _in_rect(rect, px, py) -> bool:
    return rect[0] <= px <= rect[2] and rect[1] <= py <= rect[3]


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class HUD:
    def __init__(self) -> None:
        self._fonts: dict = {}

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
        if anchor == "center":
            x -= surf.get_width() // 2
            y -= surf.get_height() // 2
        elif anchor in ("ne", "e"):
            x -= surf.get_width()
        screen.blit(surf, (x, y))

    def button_at(self, x: int, y: int, tool: Tool, garage: Optional[List] = None) -> Optional[str]:
        """Return button name hit by (x, y), or None."""
        if _in_rect(_BTN_ROAD, x, y):
            return "road"
        if _in_rect(_BTN_VEHICLES, x, y):
            return "vehicles"
        if _in_rect(_BTN_ROUTE, x, y):
            return "route"
        if _in_rect(_BTN_SPD_PAUSE, x, y):
            return "speed_pause"
        if _in_rect(_BTN_SPD_1, x, y):
            return "speed_1"
        if _in_rect(_BTN_SPD_2, x, y):
            return "speed_2"
        if _in_rect(_BTN_SPD_4, x, y):
            return "speed_4"
        if tool == Tool.VEHICLES:
            idx = self._vehicle_card_index(x, y)
            if idx is not None:
                return "buy_vehicle_{}".format(idx)
            if garage is not None:
                tidx = self._fleet_type_index(x, y, garage)
                if tidx is not None:
                    return "deploy_type_{}".format(tidx)
        return None

    def _vehicle_card_index(self, x: int, y: int) -> Optional[int]:
        if not (_POPUP_Y1 <= y <= _POPUP_Y2):
            return None
        for i in range(len(VEHICLE_DEFS)):
            cx1 = _POPUP_X1 + i * (_CARD_W + _CARD_GAP)
            cx2 = cx1 + _CARD_W
            if cx1 <= x <= cx2:
                return i
        return None

    def _fleet_type_index(self, x: int, y: int, garage: List) -> Optional[int]:
        """Return vdef index (0/1/2) if (x,y) hits an owned-type row that has count > 0."""
        if not (_FLEET_X1 <= x <= _FLEET_X2):
            return None
        owned_y0 = _POPUP_Y1 + 20
        for i, vdef in enumerate(VEHICLE_DEFS):
            row_y = owned_y0 + i * _FLEET_ROW_H
            if row_y <= y <= row_y + _FLEET_ROW_H - 2:
                count = sum(1 for v in garage if v.vdef_name == vdef["name"])
                return i if count > 0 else None
        return None

    def draw(
        self,
        screen: pygame.Surface,
        money: int,
        game_time: float,
        time_speed: TimeSpeed,
        tool: Tool,
        status: str,
        garage: Optional[List] = None,
        vehicles: Optional[List] = None,
    ) -> None:
        bar_y = _BAR_Y

        pygame.draw.rect(screen, (26, 8, 0), (0, bar_y, WINDOW_WIDTH, BOTTOM_BAR_HEIGHT))
        pygame.draw.line(screen, (192, 80, 32), (0, bar_y), (WINDOW_WIDTH, bar_y), 2)

        self._text(screen, "CREDITS", 24, bar_y + 18, 9, (255, 144, 80), bold=True)
        self._text(screen, "${:,}".format(money), 24, bar_y + 36, 20, (255, 224, 96), bold=True)

        self._draw_action_btn(screen, _BTN_ROAD,     "ROAD",     tool == Tool.ROAD)
        self._draw_action_btn(screen, _BTN_VEHICLES, "VEHICLES", tool in {Tool.VEHICLES, Tool.DEPLOY_VEHICLE_P1, Tool.DEPLOY_VEHICLE_P2})
        route_active = tool in {Tool.ROUTE_P1, Tool.ROUTE_P2}
        self._draw_action_btn(screen, _BTN_ROUTE,    "ROUTE",    route_active)

        if tool == Tool.ROUTE_P1:
            hint = "Click a city or facility entry point (first endpoint)"
        elif tool == Tool.ROUTE_P2:
            hint = "Click the second entry point"
        elif tool == Tool.DEPLOY_VEHICLE_P1:
            hint = "Click the first route endpoint on the map"
        elif tool == Tool.DEPLOY_VEHICLE_P2:
            hint = "Click the second route endpoint on the map"
        else:
            hint = status

        self._text(screen, hint, 660, bar_y + 48, 10, (255, 216, 160))

        self._draw_speed_buttons(screen, time_speed)

        total_secs = int(game_time)
        h = total_secs // 3600
        m = (total_secs % 3600) // 60
        s = total_secs % 60
        time_str = "{:02d}:{:02d}:{:02d}".format(h, m, s)
        self._text(screen, time_str, WINDOW_WIDTH - 20, bar_y + 74, 11, (200, 232, 255), bold=True, anchor="ne")

        if tool == Tool.VEHICLES:
            self._draw_vehicle_popup(screen, garage or [], vehicles or [])


    def _draw_action_btn(self, screen: pygame.Surface, rect, label: str, active: bool) -> None:
        x1, y1, x2, y2 = rect
        fill    = (208, 80, 16)  if active else (90, 32, 8)
        outline = (255, 176, 96) if active else (224, 96, 32)
        pygame.draw.rect(screen, fill,    (x1, y1, x2 - x1, y2 - y1))
        pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 2)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        self._text(screen, label, cx, cy, 12, (255, 255, 255), bold=True, anchor="center")

    def _draw_speed_buttons(self, screen: pygame.Surface, time_speed: TimeSpeed) -> None:
        specs = [
            (_BTN_SPD_PAUSE, "II",  TimeSpeed.PAUSE),
            (_BTN_SPD_1,     "1x",  TimeSpeed.NORMAL),
            (_BTN_SPD_2,     "2x",  TimeSpeed.FAST),
            (_BTN_SPD_4,     "4x",  TimeSpeed.VERY_FAST),
        ]
        for rect, label, spd in specs:
            x1, y1, x2, y2 = rect
            active  = time_speed == spd
            fill    = (176, 64, 16) if active else (58, 20, 6)
            outline = (255, 176, 96) if active else (160, 64, 16)
            pygame.draw.rect(screen, fill,    (x1, y1, x2 - x1, y2 - y1))
            pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 1)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            self._text(screen, label, cx, cy, 9, (255, 255, 255), bold=True, anchor="center")

    def _draw_vehicle_popup(self, screen: pygame.Surface, garage: List, vehicles: List) -> None:
        from src.config import VEHICLE_DEFS as _VDEFS
        card_h = _POPUP_Y2 - _POPUP_Y1
        total_w = len(_VDEFS) * (_CARD_W + _CARD_GAP) + _FLEET_W + 30

        pygame.draw.rect(screen, (22, 6, 0),   (_POPUP_X1 - 12, _POPUP_Y1 - 32, total_w + 14, card_h + 42))
        pygame.draw.rect(screen, (192, 80, 16), (_POPUP_X1 - 12, _POPUP_Y1 - 32, total_w + 14, card_h + 42), 2)

        
        self._text(screen, "Purchase:", _POPUP_X1, _POPUP_Y1 - 24, 10, (255, 144, 80), bold=True)

        for i, vdef in enumerate(_VDEFS):
            cx1 = _POPUP_X1 + i * (_CARD_W + _CARD_GAP)
            cx2 = cx1 + _CARD_W

            pygame.draw.rect(screen, (58, 18, 6),    (cx1, _POPUP_Y1, _CARD_W, card_h))
            pygame.draw.rect(screen, (208, 80, 16),  (cx1, _POPUP_Y1, _CARD_W, card_h), 2)

            swatch = _hex_to_rgb(vdef["color"])
            pygame.draw.rect(screen, swatch,          (cx1 + 10, _POPUP_Y1 + 12, 24, 24))
            pygame.draw.rect(screen, (255, 255, 255), (cx1 + 10, _POPUP_Y1 + 12, 24, 24), 1)

            self._text(screen, vdef["name"],  cx1 + 42, _POPUP_Y1 + 14, 11, (255, 255, 255), bold=True)
            self._text(screen, vdef["desc"],  cx1 + 10, _POPUP_Y1 + 50, 9,  (255, 176, 128))
            self._text(screen, "${:,}".format(vdef["cost"]), cx1 + 10, _POPUP_Y1 + 74, 13, (255, 224, 96), bold=True)
            self._text(screen, "Spd {:.1f}  Cap {}".format(vdef["speed"], vdef["capacity"]),
                       cx1 + 10, _POPUP_Y1 + 96, 8, (180, 140, 100))
            self._text(screen, "Click to buy", (cx1 + cx2) // 2, _POPUP_Y2 - 16, 8, (255, 128, 64), anchor="center")

        
        pygame.draw.line(screen, (192, 80, 32),
                         (_FLEET_X1 - 12, _POPUP_Y1 - 28), (_FLEET_X1 - 12, _POPUP_Y2), 1)

        owned_y0  = _POPUP_Y1 + 20         
        active_y0 = owned_y0 + len(_VDEFS) * _FLEET_ROW_H + 18   
        self._text(screen, "OWNED",     _FLEET_X1, _POPUP_Y1 + 4,  9, (255, 144, 80), bold=True)
        self._text(screen, "ON ROUTES", _FLEET_X1, active_y0 - 14, 9, (255, 144, 80), bold=True)
        pygame.draw.line(screen, (160, 60, 20),
                         (_FLEET_X1, active_y0 - 16), (_FLEET_X2, active_y0 - 16), 1)

        for i, vdef in enumerate(_VDEFS):
            color    = _hex_to_rgb(vdef["color"])
            n_owned  = sum(1 for v in garage   if v.vdef_name == vdef["name"])
            n_active = sum(1 for v in vehicles if v.vdef_name == vdef["name"])

            oy = owned_y0 + i * _FLEET_ROW_H
            if n_owned > 0:
                pygame.draw.rect(screen, (75, 28, 8), (_FLEET_X1, oy, _FLEET_W, _FLEET_ROW_H - 2))
            pygame.draw.rect(screen, color, (_FLEET_X1 + 4, oy + 5, 10, 10))
            name_col = (255, 255, 255) if n_owned > 0 else (100, 70, 50)
            self._text(screen, vdef["name"], _FLEET_X1 + 18, oy + 4, 9, name_col)
            count_col = (255, 200, 60) if n_owned > 0 else (80, 55, 35)
            self._text(screen, "\xd7{}".format(n_owned), _FLEET_X2 - 4, oy + 4, 9, count_col, bold=True, anchor="ne")
            if n_owned > 0:
                self._text(screen, "deploy \u25b6", _FLEET_X1 + 18, oy + 14, 7, (255, 110, 40))

            ay = active_y0 + i * _FLEET_ROW_H
            if n_active > 0:
                pygame.draw.rect(screen, (20, 50, 20), (_FLEET_X1, ay, _FLEET_W, _FLEET_ROW_H - 2))
            pygame.draw.rect(screen, color, (_FLEET_X1 + 4, ay + 5, 10, 10))
            name_col2 = (200, 255, 200) if n_active > 0 else (60, 80, 60)
            self._text(screen, vdef["name"], _FLEET_X1 + 18, ay + 4, 9, name_col2)
            count_col2 = (100, 230, 100) if n_active > 0 else (50, 80, 50)
            self._text(screen, "\xd7{}".format(n_active), _FLEET_X2 - 4, ay + 4, 9, count_col2, bold=True, anchor="ne")
