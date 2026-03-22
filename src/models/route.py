@dataclass
class Route:
    #for the game to identify the route
    id: int
    name: str   
    #the two endpoints of the route
    endpoint_a: Tuple[int, int]      
    endpoint_b: Tuple[int, int]
    path: List[Tuple[int, int]] = field(default_factory=list)
    #the route is profitable for now if it goes city to facility only
    profitable: bool = False
    