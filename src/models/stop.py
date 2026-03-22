from dataclasses import dataclass


@dataclass
class Stop:
    id: int
    name: str
    x: int
    y: int
    zone_name: str
