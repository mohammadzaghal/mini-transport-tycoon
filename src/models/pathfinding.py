from __future__ import annotations

from collections import deque
from typing import List, Tuple

from src.models.grid import Grid


def find_road_path(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    if start == goal:
        return [start]

    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        cx, cy = current
        for neighbor in grid.neighbors4(cx, cy):
            pos = (neighbor.x, neighbor.y)
            if pos in came_from:
                continue
            if not neighbor.is_driveable and pos != goal:
                continue
            came_from[pos] = current
            queue.append(pos)