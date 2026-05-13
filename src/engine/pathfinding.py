from __future__ import annotations
from collections import deque
from typing import List, Tuple
from src.models.grid import Grid


def find_road_path(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Find the shortest road path between two tile coordinates using BFS.

    Only tiles where ``Tile.is_driveable`` is True are traversed, except for
    the goal tile which is always included regardless of type (allowing routes
    to end at facility entry points or stops).

    Args:
        grid: The game grid to search.
        start: The (x, y) coordinate of the starting tile.
        goal: The (x, y) coordinate of the destination tile.

    Returns:
        An ordered list of (x, y) coordinates from ``start`` to ``goal``
        (inclusive), or an empty list if no path exists.
    """
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

    if goal not in came_from:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path

def find_track_path(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Find the shortest rail path between two tile coordinates using BFS.

    Traversable tiles include those where ``Tile.is_track_driveable`` is True,
    facility entry points, and stop tiles.  The goal tile is always reachable
    regardless of type.

    Args:
        grid: The game grid to search.
        start: The (x, y) coordinate of the starting tile.
        goal: The (x, y) coordinate of the destination tile.

    Returns:
        An ordered list of (x, y) coordinates from ``start`` to ``goal``
        (inclusive), or an empty list if no path exists.
    """
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

            traversable = (
                neighbor.is_track_driveable
                or pos == goal
                or neighbor.is_entry_point
                or neighbor.is_stop
            )
            if not traversable:
                continue

            came_from[pos] = current
            queue.append(pos)

    if goal not in came_from:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path