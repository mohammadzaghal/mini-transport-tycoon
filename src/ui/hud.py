from __future__ import annotations

from typing import Optional, List

import pygame

from src.config import BOTTOM_BAR_HEIGHT, VEHICLE_DEFS, VEHICLE_LEVEL_DEFS, WINDOW_HEIGHT, WINDOW_WIDTH
from src.ui.fonts import font_ui
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
        self.selected_bridge_type: BridgeType = BridgeType.WOODEN

    def _font(self, size: int, bold: bool = False) -> pygame.font.Font:
        return font_ui(size, bold=bold)

    def _text(self, screen, text, x, y, size, color, bold=False, anchor="nw"):
        surf = self._font(size, bold).render(text, True, color)
        if anchor == "center":
            x -= surf.get_width() // 2
            y -= surf.get_height() // 2
        elif anchor in ("ne", "e"):
            x -= surf.get_width()
        screen.blit(surf, (x, y))


    def button_at(
        self,
        x: int,
        y: int,
        tool: Tool,
        garage: Optional[List] = None,
        routes: Optional[List] = None,
    ) -> Optional[str]:
        if _in_rect(_BTN_ROAD,     x, y): return "road"
        if _in_rect(_BTN_TRACK,    x, y): return "track"
        if _in_rect(_BTN_VEHICLES, x, y): return "vehicles"
        if _in_rect(_BTN_ROUTE,    x, y): return "route"
        if _in_rect(_BTN_STOP,     x, y): return "stop"
        if _in_rect(_BTN_BRIDGE,   x, y): return "bridge"
        if _in_rect(_BTN_BULLDOZE, x, y): return "bulldoze"
        if _in_rect(_BTN_GARAGE,   x, y): return "garage"
        if _in_rect(_BTN_SPD_PAUSE, x, y): return "speed_pause"
        if _in_rect(_BTN_SPD_1,     x, y): return "speed_1"
        if _in_rect(_BTN_SPD_2,     x, y): return "speed_2"
        if _in_rect(_BTN_SPD_4,     x, y): return "speed_4"

        if tool == Tool.BRIDGE:
            if _in_rect(_BTN_BRIDGE_L1, x, y): return "bridge_wooden"
            if _in_rect(_BTN_BRIDGE_L2, x, y): return "bridge_stone"
            if _in_rect(_BTN_BRIDGE_L3, x, y): return "bridge_steel"

        if tool == Tool.VEHICLES:
            idx = self._vehicle_card_index(x, y)
            if idx is not None:
                return "buy_vehicle_{}".format(idx)
            if garage is not None:
                tidx = self._fleet_type_index(x, y, garage)
                if tidx is not None:
                    return "deploy_type_{}".format(tidx)

        if tool in {Tool.ROUTE_P1, Tool.ROUTE_P2} and routes is not None:
            action = self._routes_panel_action(x, y, routes)
            if action is not None:
                return action

        return None

    def is_in_garage_panel(self, x: int, y: int) -> bool:
        panel_h_max = 36 + 10 * _GARAGE_ROW_H + 10
        return (
            _GARAGE_PANEL_X - 4 <= x <= _GARAGE_PANEL_X + _GARAGE_PANEL_W + 8
            and _GARAGE_PANEL_Y - 4 <= y <= _GARAGE_PANEL_Y + panel_h_max + 8
        )

    def garage_panel_button_at(self, x: int, y: int, garage_vehicles: List) -> Optional[str]:
        if not garage_vehicles:
            return None
        px2 = _GARAGE_PANEL_X + _GARAGE_PANEL_W
        close_x = _GARAGE_PANEL_X + _GARAGE_PANEL_W - 20
        close_y = _GARAGE_PANEL_Y + 4
        if close_x <= x <= close_x + 18 and close_y <= y <= close_y + 16:
            return "close_garage_panel"
        for i in range(len(garage_vehicles)):
            ry = _GARAGE_PANEL_Y + 28 + i * _GARAGE_ROW_H
            if ry <= y <= ry + _GARAGE_ROW_H - 2:
                upg_x1 = px2 - 128
                upg_x2 = px2 - 68
                sell_x1 = px2 - 63
                sell_x2 = px2 - 4
                if upg_x1 <= x <= upg_x2:
                    return "upgrade_vehicle_{}".format(i)
                if sell_x1 <= x <= sell_x2:
                    return "sell_vehicle_{}".format(i)
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
        if not (_FLEET_X1 <= x <= _FLEET_X2):
            return None
        owned_y0 = _POPUP_Y1 + 20
        for i, vdef in enumerate(VEHICLE_DEFS):
            row_y = owned_y0 + i * _FLEET_ROW_H
            if row_y <= y <= row_y + _FLEET_ROW_H - 2:
                count = sum(1 for v in garage if v.vdef_name == vdef["name"])
                return i if count > 0 else None
        return None

    def _routes_panel_action(self, x: int, y: int, routes: List) -> Optional[str]:
        if not routes:
            return None
        px1 = _ROUTES_PANEL_X
        px2 = _ROUTES_PANEL_X + _ROUTES_PANEL_W
        if not (px1 <= x <= px2):
            return None
        for i, route in enumerate(routes):
            ry = _ROUTES_PANEL_Y + 26 + i * _ROUTES_ROW_H
            if ry <= y <= ry + _ROUTES_ROW_H - 2:
                bx1 = px2 - 60
                bx2 = px2 - 4
                if bx1 <= x <= bx2:
                    return "remove_route_{}".format(route.id)
        return None

    def draw(
        self,
        screen: pygame.Surface,
        money: int,
        oil: int = 0,
        iron_ore: int = 0,
        alloy_ore: int = 0,
        titanium_ore: int = 0,
        game_time: float = 0.0,
        time_speed: TimeSpeed = TimeSpeed.NORMAL,
        tool: Tool = Tool.NONE,
        status: str = "",
        garage: Optional[List] = None,
        vehicles: Optional[List] = None,
        stops: Optional[List] = None,
        routes: Optional[List] = None,
        garage_panel_tile: Optional[tuple] = None,
        garage_vehicles: Optional[List] = None,
    ) -> None:
        bar_y = _BAR_Y

        pygame.draw.rect(screen, (18, 10, 8), (0, bar_y, WINDOW_WIDTH, BOTTOM_BAR_HEIGHT))
        pygame.draw.line(screen, (160, 80, 30), (0, bar_y), (WINDOW_WIDTH, bar_y), 2)

        self._text(screen, "CREDITS", WINDOW_WIDTH - 8, bar_y + 8, 9, (255, 180, 80),
                   bold=True, anchor="ne")
        self._text(screen, "${:,}".format(money), WINDOW_WIDTH - 8, bar_y + 24, 20,
                   (255, 224, 96) if money >= 0 else (255, 80, 80), bold=True, anchor="ne")
        fuel_col = (100, 240, 255) if oil > 0 else (80, 100, 110)
        self._text(screen, "FUEL: {}".format(int(oil)), WINDOW_WIDTH - 8, bar_y + 50, 9,
                   fuel_col, bold=True, anchor="ne")
        ore_col = (255, 200, 120)
        self._text(screen, "Fe: {}  Al: {}  Ti: {}".format(int(iron_ore), int(alloy_ore), int(titanium_ore)),
                   WINDOW_WIDTH - 8, bar_y + 63, 11, ore_col, bold=True, anchor="ne")

        total_secs = int(game_time)
        h = total_secs // 3600
        m = (total_secs % 3600) // 60
        s = total_secs % 60
        day = total_secs // 60 + 1
        self._text(screen, "SOL {:d}  {:02d}:{:02d}:{:02d}".format(day, h, m, s),
                   WINDOW_WIDTH - 8, bar_y + 90, 9, (200, 180, 140), bold=True, anchor="ne")

        hint = self._hint_text(tool, status)
        self._text(screen, hint, WINDOW_WIDTH // 2, bar_y + 8, 10, (180, 210, 160), anchor="center")

        self._draw_action_btn(screen, _BTN_ROAD,     "ROAD[R]",  tool == Tool.ROAD)
        self._draw_action_btn(screen, _BTN_TRACK,    "RAIL[T]",  tool == Tool.TRACK)
        self._draw_action_btn(screen, _BTN_VEHICLES, "FLEET",    tool in {Tool.VEHICLES, Tool.DEPLOY_VEHICLE_P1, Tool.DEPLOY_VEHICLE_P2})
        self._draw_action_btn(screen, _BTN_ROUTE,    "ROUTE",    tool in {Tool.ROUTE_P1, Tool.ROUTE_P2})
        self._draw_action_btn(screen, _BTN_STOP,     "STOP[S]",  tool == Tool.STOP)
        self._draw_action_btn(screen, _BTN_BRIDGE,   "BRIDGE[K]",tool == Tool.BRIDGE)
        self._draw_action_btn(screen, _BTN_BULLDOZE, "DEMO[B]",  tool == Tool.BULLDOZE)
        self._draw_action_btn(screen, _BTN_GARAGE,   "GARAGE[G]",tool == Tool.GARAGE)

        if tool == Tool.BRIDGE:
            self._draw_bridge_sub(screen)

        self._draw_speed_buttons(screen, time_speed)

        if tool == Tool.VEHICLES:
            self._draw_vehicle_popup(screen, garage or [], vehicles or [])

        if tool in {Tool.ROUTE_P1, Tool.ROUTE_P2}:
            self._draw_routes_panel(screen, routes or [])

        if garage_panel_tile is not None:
            self._draw_garage_panel(screen, garage_vehicles or [])