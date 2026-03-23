from __future__ import annotations

from typing import Optional, List

import pygame

from src.config import BOTTOM_BAR_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH
from src.enums import Tool


_BAR_Y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT

_BTN_Y1 = _BAR_Y + 18
_BTN_Y2 = _BAR_Y + 88

_BTN_ROAD      = (250,  _BTN_Y1, 360,  _BTN_Y2)
_BTN_VEHICLES  = (380,  _BTN_Y1, 510,  _BTN_Y2)
_BTN_ROUTE     = (530,  _BTN_Y1, 640,  _BTN_Y2)


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
        route_active = False
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

    def _draw_action_btn(self, screen: pygame.Surface, rect, label: str, active: bool) -> None:
        x1, y1, x2, y2 = rect
        fill = (208, 80, 16) if active else (90, 32, 8)
        outline = (255, 176, 96) if active else (224, 96, 32)
        pygame.draw.rect(screen, fill, (x1, y1, x2 - x1, y2 - y1))
        pygame.draw.rect(screen, outline, (x1, y1, x2 - x1, y2 - y1), 2)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        self._text(screen, label, cx, cy, 12, (255, 255, 255), bold=True, anchor="center")