import pygame

from src.config import (
    MAP_HEIGHT,
    MAP_WIDTH,
    TILE_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    BOTTOM_BAR_HEIGHT,
    STARTING_MONEY,
)
from src.engine.camera import Camera
from src.engine.map_generator import MapGenerator
from src.models.company import Company
from src.models.grid import Grid
from src.render.map_renderer import MapRenderer


FPS = 60


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Transport Tycoon")

        self.clock = pygame.time.Clock()
        self.running = True

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.company = Company("Player Co.", STARTING_MONEY)

        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE,
            view_width=WINDOW_WIDTH,
            view_height=WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
        )

        MapGenerator(seed=7).generate(self.grid)

        self.renderer = MapRenderer()
        self.renderer.build_map_image(self.grid)


    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update(dt)

            self.draw()
            pygame.display.flip()

        pygame.quit()


    def update(self, dt: float) -> None:
        pass


    def draw(self) -> None:
        self.renderer.draw(
            self.screen,
            self.grid,
            self.camera,
            routes=[],
            vehicles=[],
            hover_tile=None,
        )