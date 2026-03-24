import tkinter as tk

from src.config import (
    BOTTOM_BAR_HEIGHT,
    MAP_HEIGHT,
    MAP_WIDTH,
    TILE_SIZE,
    TOP_BAR_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.engine.camera import Camera
from src.engine.map_generator import MapGenerator
from src.enums import TileType
from src.models.grid import Grid


_TILE_COLORS = {
    TileType.GRASS: "#2d6a2d",
    TileType.FOREST: "#1d4a1d",
    TileType.WATER: "#2a4a7a",
    TileType.ROAD: "#5c5c5c",
    TileType.CITY: "#8a3a3a",
    TileType.FACILITY: "#8a6a2a",
}


class Game:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Transport Tycoon (minimal map view)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.company = Company("Ares Colony Logistics", STARTING_MONEY)

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#12060a",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.stops = MapGenerator(seed=7).generate(self.grid)

        view_h = WINDOW_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE + TOP_BAR_HEIGHT,
            view_width=WINDOW_WIDTH,
            view_height=view_h,
        )

        self.root.bind("<KeyPress>", self._on_key)

    def _build_road(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if not self.grid.is_road_buildable(x, y):
            self.status_message = "Can only build roads on grass or forest tiles."
            return
        cost = ROAD_COST + (FOREST_CLEAR_COST if tile.tile_type == TileType.FOREST else 0)
        if not self.company.spend(cost):
            self.status_message = "Not enough credits to build road (need ${}).".format(cost)
            return
        tile.tile_type = TileType.ROAD
        tile.tree_count = 0
        self.renderer.update_tile(x, y, tile)
        self.status_message = "Road built at ({},{}) for ${}.".format(x, y, cost)

    def _bulldoze(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type == TileType.ROAD and not tile.is_entry_point:
            for route in self.routes:
                if (x, y) in route.path:
                    self._dissolve_route(route)
                    return
            tile.tile_type = TileType.GRASS
            tile.is_route_road = False
            self.renderer.update_tile(x, y, tile)
            self.status_message = "Road removed at ({},{}).".format(x, y)


    def _on_key(self, event) -> None:
        step = TILE_SIZE
        if event.keysym in ("Left", "a", "A"):
            self.camera.move(-step, 0)
        elif event.keysym in ("Right", "d", "D"):
            self.camera.move(step, 0)
        elif event.keysym in ("Up", "w", "W"):
            self.camera.move(0, -step)
        elif event.keysym in ("Down", "s", "S"):
            self.camera.move(0, step)
        self._draw()

    def _draw(self) -> None:
        self.canvas.delete("all")
        ts = TILE_SIZE
        for tile in self.grid.iter_tiles():
            wx = tile.x * ts
            wy = tile.y * ts + TOP_BAR_HEIGHT
            sx, sy = self.camera.world_to_screen(wx, wy)
            color = _TILE_COLORS.get(tile.tile_type, "#333333")
            self.canvas.create_rectangle(
                sx, sy, sx + ts, sy + ts, fill=color, outline="#1a0a08", width=1
            )

    def run(self) -> None:
        self._draw()
        self.root.mainloop()

        