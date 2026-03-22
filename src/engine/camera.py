class Camera:
    def __init__(self, map_width_px: int, map_height_px: int, view_width: int, view_height: int) -> None:
        self.map_width_px = map_width_px
        self.map_height_px = map_height_px
        self.view_width = view_width
        self.view_height = view_height
        self.x = 0
        self.y = 0

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
        self.clamp()

    def clamp(self) -> None:
        max_x = max(0, self.map_width_px - self.view_width)
        max_y = max(0, self.map_height_px - self.view_height)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def world_to_screen(self, world_x: int, world_y: int) -> tuple[int, int]:
        return world_x - self.x, world_y - self.y

    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        return screen_x + self.x, screen_y + self.y
