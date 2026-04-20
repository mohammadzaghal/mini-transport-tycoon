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
        self.selected_bridge_type: BridgeType = BridgeType.WOODEN

    def _font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont("segoeui", size, bold=bold)
        return self._fonts[key]

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

        if tool in {Tool.ROUTE_P1, Tool.ROUTE_P2} and routes is not None:  # v1.1 #14
            action = self._routes_panel_action(x, y, routes)
            if action is not None:
                return action

        return None



  def is_in_garage_panel(self, x: int, y: int) -> bool:        # v1.1 #13
        """Return True if (x, y) falls within the garage upgrade panel bounds."""
        panel_h_max = 36 + 10 * _GARAGE_ROW_H + 10
        return (
            _GARAGE_PANEL_X - 4 <= x <= _GARAGE_PANEL_X + _GARAGE_PANEL_W + 8
            and _GARAGE_PANEL_Y - 4 <= y <= _GARAGE_PANEL_Y + panel_h_max + 8
        )

    def garage_panel_button_at(self, x: int, y: int, garage_vehicles: List) -> Optional[str]:  # v1.1 #13
        """Hit-test for the garage upgrade panel buttons."""
        if not garage_vehicles:
            return None
        px2 = _GARAGE_PANEL_X + _GARAGE_PANEL_W
        # Close button
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

     def _routes_panel_action(self, x: int, y: int, routes: List) -> Optional[str]:  # v1.1 #14
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
        self._draw_action_btn(screen, _BTN_TRACK,    "RAIL[T]",  tool == Tool.TRACK)  # v1.1 #18
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



def _hint_text(self, tool: Tool, status: str) -> str:
        hints = {
            Tool.ROAD:              "Click tiles to build dust roads  [ESC to cancel]",
            Tool.TRACK:             "Click tiles to lay mag-rails  [ESC to cancel]",
            Tool.ROUTE_P1:          "Click FIRST entry point (◆) or stop (S)",
            Tool.ROUTE_P2:          "Click SECOND entry point (◆) or stop (S)",
            Tool.STOP:              "Click a road or rail tile to place a stop  [ESC to cancel]",
            Tool.BRIDGE:            "Select bridge level below, then click an ICE tile",
            Tool.BULLDOZE:          "1st click: remove route (road stays). 2nd click: remove tile.",
            Tool.GARAGE:            "Click an open regolith tile to build a garage  [ESC to cancel]",
            Tool.DEPLOY_VEHICLE_P1: "Click FIRST route endpoint",
            Tool.DEPLOY_VEHICLE_P2: "Click SECOND route endpoint",
        }
        return hints.get(tool, status)




    def _draw_action_btn(self, screen: pygame.Surface, rect, label: str, active: bool) -> None:
        x1, y1, x2, y2 = rect
        fill    = (208, 80, 16)  if active else (90, 32, 8)
        outline = (255, 176, 96) if active else (224, 96, 32)
        pygame.draw.rect(screen, fill,    (x1, y1, x2 - x1, y2 - y1))
        pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 2)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        self._text(screen, label, cx, cy, 12, (255, 255, 255), bold=True, anchor="center")

       def _draw_bridge_sub(self, screen: pygame.Surface) -> None:   # v1.1 #7
        specs = [
            (_BTN_BRIDGE_L1, "L1 BASIC\n10 Fe · Hauler", BridgeType.WOODEN),
            (_BTN_BRIDGE_L2, "L2 REIN\n10 Al · +Rover", BridgeType.STONE),
            (_BTN_BRIDGE_L3, "L3 MAG\n10 Ti · +Maglev", BridgeType.STEEL),
        ]
        for rect, label, bt in specs:
            x1, y1, x2, y2 = rect
            active = self.selected_bridge_type == bt
            fill    = (60, 90, 130) if active else (25, 40, 60)
            outline = (120, 180, 255) if active else (60, 90, 130)
            pygame.draw.rect(screen, fill,    (x1, y1, x2 - x1, y2 - y1), border_radius=3)
            pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 2, border_radius=3)
            cx = (x1 + x2) // 2
            line1, line2 = label.split("\n")
            self._text(screen, line1, cx, y1 + 5, 9, (200, 220, 255), bold=True, anchor="center")
            self._text(screen, line2, cx, y1 + 19, 8, (160, 200, 255), anchor="center")


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
