# Mini Transport Tycoon — Software Specification

## 1. Project Overview

**Mini Transport Tycoon** is a 2D top-down economic simulation game inspired by the classic OpenTTD / Transport Tycoon Deluxe series.  Players build transport networks on a procedurally generated Mars-themed map, deploy vehicles to carry cargo and passengers between industrial facilities and cities, and grow their company by maximising profit.

| Attribute | Value |
|-----------|-------|
| Team | Dana Al Tamimi, Mohammed Alzaghal, Tiya Kumar |
| Language | Python 3.11+ |
| Graphics framework | Pygame-CE 2.5+ |
| Test framework | pytest + pytest-cov |
| Target platform | Windows / Linux (desktop) |

---

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The player shall be able to build road tiles on GRASS and FOREST terrain. |
| FR-02 | The player shall be able to build rail track tiles on GRASS, FOREST, and existing ROAD or TRACK terrain. |
| FR-03 | The player shall be able to build stops on existing ROAD or TRACK tiles so vehicles can load and unload. |
| FR-04 | The player shall be able to build bridges over WATER tiles in three upgrade levels (Wooden, Stone, Steel), each paid for with ore resources. |
| FR-05 | The player shall be able to demolish player-built roads, tracks, stops, bridges, and garages using the bulldoze tool. |
| FR-06 | The player shall be able to build vehicle garages on GRASS or FOREST tiles. |
| FR-07 | The player shall be able to purchase vehicles of three types: Rover (bus, road), Hauler (truck, road), and Maglev (train, rail). |
| FR-08 | The player shall be able to define circular routes between two endpoints by clicking map entry points or stops. |
| FR-09 | The system shall automatically find the shortest BFS path for a route between its two endpoints. |
| FR-10 | Vehicles shall autonomously follow their assigned route in a continuous loop, loading and unloading cargo at stops and facility entry points. |
| FR-11 | Industrial facilities shall produce cargo at a continuous rate; each tick advances production by the elapsed simulated time. |
| FR-12 | Cities shall accumulate growth points each time a vehicle delivers cargo to them, and expand onto adjacent tiles once enough points are collected. |
| FR-13 | Vehicles shall require periodic maintenance; failure to service them increases cost proportionally to their age. |
| FR-14 | The company shall go bankrupt and the game shall end if the cash balance drops below zero. |
| FR-15 | The player shall be able to upgrade vehicles up to level 3 using fuel (oil) resources to increase speed and capacity. |
| FR-16 | The player shall be able to sell vehicles from the garage panel for a fraction of their purchase price. |
| FR-17 | The map shall be procedurally generated from a seed, producing consistent layouts across runs with the same seed. |
| FR-18 | The camera shall scroll with WASD / arrow keys, mouse wheel, and clicking the minimap. |
| FR-19 | The simulation speed shall be adjustable (Pause, 1×, 2×, 4×) via the HUD. |
| FR-20 | A "How to Play" help overlay shall be accessible from the start screen. |
| FR-21 | Contextual hint text shall be displayed in the HUD for the currently active tool. |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NF-01 | The game shall maintain a stable 20 FPS render target (50 ms tick). |
| NF-02 | Map size: 80 × 55 tiles at 32 px per tile (2,560 × 1,760 world pixels). |
| NF-03 | Window resolution: 1,280 × 700 pixels with a 100 px HUD bar at the bottom. |
| NF-04 | Test coverage of the `src/models/` and `src/engine/` layers shall be ≥ 80 %. |
| NF-05 | The CI/CD pipeline shall run linting, tests, and documentation generation on every push. |
| NF-06 | All public and protected interfaces shall carry Google-style docstrings extractable by pdoc3. |
| NF-07 | Code shall follow PEP 8 conventions; line length shall not exceed 120 characters. |

---

## 4. System Architecture

The codebase is organised into five layers:

```
src/
├── models/       — Pure data layer (dataclasses, no rendering or I/O)
├── engine/       — Business-logic layer (map generation, pathfinding, city growth, camera)
├── render/       — Rendering layer (MapRenderer, Minimap)
├── ui/           — User-interface layer (HUD, StartScreen, fonts)
└── game.py       — Orchestrator — owns all subsystems and runs the game loop
```

### Layer responsibilities

| Layer | Responsibilities | Key classes |
|-------|-----------------|-------------|
| **models** | Store game state as immutable-style dataclasses; no rendering | `Company`, `Vehicle`, `Grid`, `Tile`, `Route`, `Stop`, `Garage`, `Facility` |
| **engine** | Algorithms and game-world rules | `MapGenerator`, `find_road_path`, `find_track_path`, `CityGrowthManager`, `Camera` |
| **render** | Draw the map and overlays to pygame surfaces | `MapRenderer`, `Minimap` |
| **ui** | Draw the HUD and menus; translate clicks to action strings | `HUD`, `StartScreen` |
| **game.py** | Own all instances; run the frame loop; route actions to the right subsystem | `Game` |

### Key data flows

1. **Build action**: Player clicks → `Game._build_road(x, y)` → `Grid.set_tile_type` → `MapRenderer.update_tile` → `Minimap.update_tile`
2. **Vehicle update**: `Game.update(dt)` → `Vehicle.update(dt)` → if stop reached → `Game._handle_vehicle_at_stop(vehicle, tile)`
3. **City growth**: delivery recorded → `CityGrowthManager.on_delivery(city)` → on next tick `CityGrowthManager.tick(grid, renderer, minimap)`

---

## 5. Data Model

```
Game
 ├── Grid (80 × 55 Tile objects)
 │    └── Tile  → optional: Stop, Garage, Facility refs
 ├── Company
 ├── Camera
 ├── CityGrowthManager
 ├── List[Route]
 │    └── Route { endpoint_a, endpoint_b, path[], stop_positions[], path_type }
 ├── List[Vehicle]  (deployed, on routes)
 │    └── Vehicle { VehicleType, path, cargo_on_board: Dict[CargoType, float] }
 ├── List[Vehicle]  (garage, not yet deployed)
 ├── List[Stop]
 ├── List[Garage]
 └── Dict[str, Facility]
      └── Facility { FacilityType, inventory: Dict[CargoType, float] }
```

### Enum summary

| Enum | Values |
|------|--------|
| `TileType` | GRASS, FOREST, ROAD, TRACK, CITY, FACILITY, WATER |
| `CargoType` | IRON_ORE, ALLOY_ORE, TITANIUM_ORE, FUEL, AQUATICS, CRYSTALS |
| `FacilityType` | ORE_MINE, FUEL_RIG, AQUA_DOME, CRYSTAL_LAB |
| `VehicleType` | BUS (Rover), TRUCK (Hauler), TRAIN (Maglev) |
| `BridgeType` | WOODEN (L1), STONE (L2), STEEL (L3) |
| `TimeSpeed` | PAUSE (0×), NORMAL (1×), FAST (2×), VERY_FAST (4×) |
| `Tool` | NONE, ROAD, TRACK, ROUTE_P1/P2, VEHICLES, DEPLOY_P1/P2, BULLDOZE, STOP, BRIDGE, GARAGE |

---

## 6. Game Balance Parameters

All values are defined in [src/config.py](src/config.py) and can be adjusted without touching logic code.

| Parameter | Value | Design rationale |
|-----------|-------|-----------------|
| Starting money | 20,000 | Enough for 3–4 short roads and 1–2 vehicles before first revenue |
| Road cost | 100 | Affordable for early-game expansion |
| Track cost | 150 | Small premium over roads to reflect rail infrastructure |
| Forest clear surcharge | 50 | Discourages route building through dense forest |
| Garage cost | 2,000 | Significant investment; players should earn revenue before expanding |
| Rover (bus) cost | 1,200 | Cheapest vehicle; suited for short passenger routes |
| Hauler (truck) cost | 800 | Cheapest overall; freight focus, slower than bus |
| Maglev (train) cost | 2,500 | High capacity (60), track-only; justified for long mineral routes |
| Maintenance interval | 30 simulated days | Forces regular cash planning; neglect = exponential cost |
| City growth threshold | 200 points | ~20 deliveries per expansion; gradual city spread |
| Points per delivery | 10 | One delivery = 5% progress toward expansion |
| Facility max stock | 200 units | Prevents facilities from accumulating infinite backlog |
| Bridge ore costs | 10 units per level | Bridges require ore investment proportional to vehicle support |

### Bridge vehicle support

| Bridge level | Ore cost | Supports |
|---|---|---|
| Wooden | 10 Iron Ore | Trucks only |
| Stone | 10 Alloy Ore | Trucks + Buses |
| Steel | 10 Titanium Ore | All vehicles (including Maglev) |

---

## 7. Changes from Original Specification

The following changes were made relative to the plans submitted in Milestone 1:

| Feature | Original plan | Final implementation | Reason |
|---------|--------------|---------------------|--------|
| Map generation | Full Wave Function Collapse (WFC) | Seeded-random placement with legacy fallback positions | WFC proved too complex to tune within the milestone timeline; the fallback system guarantees stable, playable layouts |
| Multiplayer | Planned for a future milestone | Removed from scope; single-player only | Scope reduction to ensure quality on single-player features |
| Cargo types | Iron Ore, Alloy Ore, Titanium Ore | Added Fuel, Aquatics, Crystals | Expanded to give facilities more variety and differentiate vehicle utility |
| Bridge system | 2 bridge levels | 3 bridge levels (Wooden, Stone, Steel) | Added Wooden tier so trucks can cross water early without expensive ore |
| Vehicle upgrade | Not originally planned | Level 1–3 upgrades using fuel resource | Added to provide mid-game progression without requiring new vehicles |
| Facility consumption | Facilities consume inputs to produce outputs | Removed consumption (all facilities produce autonomously) | Simplified to avoid soft-lock scenarios where cargo couldn't reach consumers |
| City water requirement | Cities require Aquatics delivery to unlock growth | Removed hard requirement; Aquatics is just a delivery cargo type | Reduced frustration for players who hadn't yet built Aqua Dome routes |

---

## 8. Generating API Documentation

The HTML API manual is generated from docstrings using **pdoc3**.

```bash
# Install (one-time)
pip install pdoc3

# Generate HTML into docs/ folder
python -m pdoc --html --output-dir docs/ src/

# Open in browser
start docs/src/index.html        # Windows
open docs/src/index.html         # macOS
xdg-open docs/src/index.html     # Linux
```

The `docs/` folder is also produced automatically by the CI/CD pipeline and uploaded as an artifact named `api-docs` on every push to GitHub.

---

## 9. Running the Game and Tests

```bash
# Install runtime dependency
pip install pygame-ce

# Run the game
python main.py

# Run all unit tests
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Run tests excluding slow pygame integration tests
pytest -m "not slow"
```



#Run all here
pip install -r requirements.txt
