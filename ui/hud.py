from __future__ import annotations

from typing import Optional, List

import pygame

from src.config import BOTTOM_BAR_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH
from src.enums import TimeSpeed, Tool


_BAR_Y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT

_BTN_Y1 = _BAR_Y + 18
_BTN_Y2 = _BAR_Y + 88

_BTN_ROAD      = (250,  _BTN_Y1, 360,  _BTN_Y2)
_BTN_VEHICLES  = (380,  _BTN_Y1, 510,  _BTN_Y2)
_BTN_ROUTE     = (530,  _BTN_Y1, 640,  _BTN_Y2)

# Speed tiny buttons (bottom-right area)
_SPD_Y1 = _BAR_Y + 35
_SPD_Y2 = _BAR_Y + 62
_SPD_X  = WINDOW_WIDTH - 260
_BTN_SPD_PAUSE = (_SPD_X,       _SPD_Y1, _SPD_X + 38,  _SPD_Y2)
_BTN_SPD_1     = (_SPD_X + 42,  _SPD_Y1, _SPD_X + 80,  _SPD_Y2)
_BTN_SPD_2     = (_SPD_X + 84,  _SPD_Y1, _SPD_X + 122, _SPD_Y2)
_BTN_SPD_4     = (_SPD_X + 126, _SPD_Y1, _SPD_X + 164, _SPD_Y2)


def _in_rect(rect, px, py) -> bool:
    return rect[0] <= px <= rect[2] and rect[1] <= py <= rect[3]


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
        return None

    def draw(
        self,
        screen: pygame.Surface,
        money: int,
        game_time,
        time_speed,
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

        self._draw_action_btn(screen, _BTN_ROAD, "ROAD", tool == Tool.ROAD)
        self._draw_action_btn(screen, _BTN_VEHICLES, "VEHICLES", tool == Tool.VEHICLES)
        route_active = tool in {Tool.ROUTE_P1, Tool.ROUTE_P2}
        self._draw_action_btn(screen, _BTN_ROUTE, "ROUTE", route_active)

        hint = status
        if tool == Tool.ROUTE_P1:
            hint = "Click a city or facility entry point (first endpoint)"
        elif tool == Tool.ROUTE_P2:
            hint = "Click the second entry point"
        elif tool == Tool.DEPLOY_VEHICLE_P1:
            hint = "Click the first route endpoint on the map"
        elif tool == Tool.DEPLOY_VEHICLE_P2:
            hint = "Click the second route endpoint on the map"

        self._text(screen, hint, 660, bar_y + 48, 10, (255, 216, 160))

        self._draw_speed_buttons(screen, time_speed)

        total_secs = int(game_time)
        h = total_secs // 3600
        m = (total_secs % 3600) // 60
        s = total_secs % 60
        time_str = "{:02d}:{:02d}:{:02d}".format(h, m, s)
        self._text(
            screen,
            time_str,
            WINDOW_WIDTH - 20,
            bar_y + 74,
            11,
            (200, 232, 255),
            bold=True,
            anchor="ne",
        )

    def _draw_action_btn(self, screen: pygame.Surface, rect, label: str, active: bool) -> None:
        x1, y1, x2, y2 = rect
        fill = (208, 80, 16) if active else (90, 32, 8)
        outline = (255, 176, 96) if active else (224, 96, 32)
        pygame.draw.rect(screen, fill, (x1, y1, x2 - x1, y2 - y1))
        pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 2)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        self._text(screen, label, cx, cy, 12, (255, 255, 255), bold=True, anchor="center")

    def _draw_speed_buttons(self, screen: pygame.Surface, time_speed: TimeSpeed) -> None:
        specs = [
            (_BTN_SPD_PAUSE, "II", TimeSpeed.PAUSE),
            (_BTN_SPD_1, "1x", TimeSpeed.NORMAL),
            (_BTN_SPD_2, "2x", TimeSpeed.FAST),
            (_BTN_SPD_4, "4x", TimeSpeed.VERY_FAST),
        ]
        for rect, label, spd in specs:
            x1, y1, x2, y2 = rect
            active = time_speed == spd
            fill = (176, 64, 16) if active else (58, 20, 6)
            outline = (255, 176, 96) if active else (160, 64, 16)
            pygame.draw.rect(screen, fill, (x1, y1, x2 - x1, y2 - y1))
            pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 1)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            self._text(screen, label, cx, cy, 9, (255, 255, 255), bold=True, anchor="center")