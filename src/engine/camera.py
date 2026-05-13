from __future__ import annotations
from typing import Tuple

class Camera:
    """Manages the scrollable viewport over the game world.

    The camera tracks an (x, y) pixel offset into the world map and
    provides conversion helpers between world-space and screen-space
    coordinates.  The offset is always clamped so the viewport cannot
    scroll beyond the map boundaries.

    Attributes:
        map_width_px: Total width of the game map in pixels.
        map_height_px: Total height of the game map in pixels.
        view_width: Width of the visible viewport in pixels.
        view_height: Height of the visible viewport in pixels.
        x: Current horizontal scroll offset in pixels.
        y: Current vertical scroll offset in pixels.
    """

    def __init__(self, map_width_px: int, map_height_px: int, view_width: int, view_height: int) -> None:
        """Initialise the camera centred at the top-left corner of the map.

        Args:
            map_width_px: Total map width in pixels.
            map_height_px: Total map height in pixels.
            view_width: Viewport width in pixels.
            view_height: Viewport height in pixels.
        """
        self.map_width_px = map_width_px
        self.map_height_px = map_height_px
        self.view_width = view_width
        self.view_height = view_height
        self.x = 0
        self.y = 0

    def move(self, dx: int, dy: int) -> None:
        """Scroll the camera by a pixel delta and clamp to map boundaries.

        Args:
            dx: Horizontal displacement in pixels (positive = scroll right).
            dy: Vertical displacement in pixels (positive = scroll down).
        """
        self.x += dx
        self.y += dy
        self.clamp()

    def clamp(self) -> None:
        """Constrain the camera offset so the viewport stays within the map."""
        max_x = max(0, self.map_width_px - self.view_width)
        max_y = max(0, self.map_height_px - self.view_height)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world-space pixel coordinates to screen-space coordinates.

        Args:
            world_x: Horizontal position in world pixels.
            world_y: Vertical position in world pixels.

        Returns:
            The corresponding (screen_x, screen_y) pixel position.
        """
        return world_x - self.x, world_y - self.y

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen-space pixel coordinates to world-space coordinates.

        Args:
            screen_x: Horizontal position in screen pixels.
            screen_y: Vertical position in screen pixels.

        Returns:
            The corresponding (world_x, world_y) pixel position.
        """
        return screen_x + self.x, screen_y + self.y