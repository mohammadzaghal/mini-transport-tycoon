from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest


@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def screen():
    from src.config import WINDOW_WIDTH, WINDOW_HEIGHT
    surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    surf.fill((0, 0, 0))
    return surf


@pytest.fixture
def seeded_game(screen):
    random.seed(42)
    from src.game import Game
    return Game(screen)
