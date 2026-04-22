from __future__ import annotations

from pathlib import Path
import pygame

_FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"

_cache: dict[tuple[str, int, bool, bool], pygame.font.Font] = {}


def _safe_font(path: Path, size: int) -> pygame.font.Font:
    if not pygame.font.get_init():
        pygame.font.init()

    if path.exists():
        try:
            f = pygame.font.Font(str(path), size)
            # verify the font is actually usable (some TTFs load but render NULL)
            f.render("A", True, (0, 0, 0))
            return f
        except (pygame.error, OSError):
            pass

    try:
        return pygame.font.SysFont("Arial,Helvetica", size)
    except pygame.error:
        return pygame.font.Font(None, size)


def font_display(size: int, bold: bool = True, italic: bool = False) -> pygame.font.Font:
    key = ("display", size, bold, italic)
    if key not in _cache:
        _cache[key] = _safe_font(_FONTS_DIR / "Orbitron-Bold.ttf", size)
    return _cache[key]


def font_ui(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    key = ("ui", size, bold, italic)
    if key not in _cache:
        fname = "Nunito-Bold.ttf" if bold else "Nunito-Regular.ttf"
        _cache[key] = _safe_font(_FONTS_DIR / fname, size)
    return _cache[key]


def font_map(size: int, bold: bool = True, italic: bool = False) -> pygame.font.Font:
    key = ("map", size, bold, italic)
    if key not in _cache:
        _cache[key] = _safe_font(_FONTS_DIR / "Nunito-Bold.ttf", size)
    return _cache[key]