from __future__ import annotations

from pathlib import Path
import pygame

_FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"

_cache: dict[tuple[str, int, bool, bool], pygame.font.Font] = {}


def _load(path: Path, size: int) -> pygame.font.Font:
    if path.exists():
        return pygame.font.Font(str(path), size)
    return pygame.font.SysFont("Arial,Helvetica", size)


def font_display(size: int, bold: bool = True, italic: bool = False) -> pygame.font.Font:
    key = ("display", size, bold, italic)
    if key not in _cache:
        _cache[key] = _load(_FONTS_DIR / "Orbitron-Bold.ttf", size)
    return _cache[key]


def font_ui(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    key = ("ui", size, bold, italic)
    if key not in _cache:
        fname = "Nunito-Bold.ttf" if bold else "Nunito-Regular.ttf"
        _cache[key] = _load(_FONTS_DIR / fname, size)
    return _cache[key]


def font_map(size: int, bold: bool = True, italic: bool = False) -> pygame.font.Font:
    key = ("map", size, bold, italic)
    if key not in _cache:
        _cache[key] = _load(_FONTS_DIR / "Nunito-Bold.ttf", size)
    return _cache[key]