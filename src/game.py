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
from src.enums import TimeSpeed
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
        self.fullscreen = False

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.company = Company("Player Co.", STARTING_MONEY)

        self.time_speed = TimeSpeed.NORMAL
        self.game_time = 0.0

        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE,
            view_width=WINDOW_WIDTH,
            view_height=WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
        )

        MapGenerator(seed=7).generate(self.grid)

        self.renderer = MapRenderer()
        self.renderer.build_map_image(self.grid)

        self.mouse_pos = (0, 0)


    def run(self) -> None:
        while self.running:
            dt_ms = self.clock.tick(FPS)
            real_dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    self._on_key_down(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._on_left_press(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self._on_left_release(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    self._on_mouse_move(event.pos)

                elif event.type == pygame.MOUSEWHEEL:
                    self._on_mouse_wheel(event)

            if self.time_speed != TimeSpeed.PAUSE:
                sim_dt = real_dt * self.time_speed.value
                self.update(sim_dt)

            self.draw()
            pygame.display.flip()

        pygame.quit()


    def update(self, dt: float) -> None:
        self.game_time += dt


    def draw(self) -> None:
        self.renderer.draw(
            self.screen,
            self.grid,
            self.camera,
            routes=[],
            vehicles=[],
            hover_tile=None,
        )


    def _on_key_down(self, key: int) -> None:
        if key == pygame.K_1:
            self.time_speed = TimeSpeed.PAUSE
        elif key == pygame.K_2:
            self.time_speed = TimeSpeed.NORMAL
        elif key == pygame.K_3:
            self.time_speed = TimeSpeed.FAST
        elif key == pygame.K_4:
            self.time_speed = TimeSpeed.VERY_FAST

        elif key == pygame.K_ESCAPE:
            print("Cancel tool (placeholder)")

        elif key == pygame.K_r:
            print("Road tool selected (placeholder)")

        elif key == pygame.K_b:
            print("Bulldoze tool selected (placeholder)")

        elif key == pygame.K_F11:
            self._toggle_fullscreen()

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)


    def _on_left_press(self, pos: tuple) -> None:
        print(f"Mouse pressed at {pos}")

    def _on_left_release(self, pos: tuple) -> None:
        print(f"Mouse released at {pos}")

    def _on_mouse_move(self, pos: tuple) -> None:
        self.mouse_pos = pos

    def _on_mouse_wheel(self, event) -> None:
        scroll = event.y * 40

        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_SHIFT:
            self.camera.move(-scroll, 0)
        else:
            self.camera.move(0, -scroll)