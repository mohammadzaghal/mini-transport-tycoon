import pygame
from src.ui.start_screen import StartScreen
from src.game import Game
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT, TICK_MS

FPS = 1000 // TICK_MS


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mini Transport Tycoon")
    clock = pygame.time.Clock()

    start_screen = StartScreen()
    state = "menu"
    game: Game | None = None

    running = True
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if state == "menu":
            clock.tick(FPS)
            for event in events:
                if start_screen.handle_event(event):
                    state = "game"
                    game = Game(screen)
            start_screen.draw(screen)
            pygame.display.flip()

        elif state == "game" and game is not None:
            if not game.tick(events):
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()