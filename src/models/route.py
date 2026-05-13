from dataclasses import dataclass, field
from typing import List, Tuple 

@dataclass
class Route:
    """Defines a circular transport path between two map endpoints.

    Vehicles assigned to a route travel the ``path`` in a loop, loading and
    unloading cargo at intermediate stops and at the two endpoints.

    Attributes:
        id: Unique integer identifier for this route.
        name: Human-readable label shown in the route list panel.
        endpoint_a: The (x, y) tile coordinate of the first terminus.
        endpoint_b: The (x, y) tile coordinate of the second terminus.
        path: Ordered list of (x, y) tile coordinates forming the full loop.
        profitable: True when the route connects a city to a production facility,
            making it eligible for revenue bonuses.
        path_type: Either ``"road"`` (wheeled vehicles) or ``"track"`` (rail).
        stop_positions: List of (x, y) coordinates of intermediate stops along
            the path where vehicles pause to load/unload.
    """

    id: int
    name: str
    endpoint_a: Tuple[int, int]
    endpoint_b: Tuple[int, int]
    path: List[Tuple[int, int]] = field(default_factory=list)
    profitable: bool = False
    path_type: str = "road"
    stop_positions: List[Tuple[int, int]] = field(default_factory=list)