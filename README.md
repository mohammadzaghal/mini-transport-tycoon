# Mini Transport Tycoon

A simplified transport-economy simulation game inspired by *Transport Tycoon*, built for the Software Technology Practice course at ELTE Faculty of Informatics, 2025/2026 Spring semester.

You organise and manage a road transport network: build roads, place stops, buy vehicles, define routes, and move freight and passengers between cities and industrial facilities — profitably, or you go bankrupt.

## Team

Built by **Dana Al Tamimi**, **Mohammad Alzaghal** and **Tiya Kumar** over one semester, on the faculty GitLab with issue boards, merge requests and CI.

## Technology

Python, Pygame, pytest.

## Running it

```bash
pip install -r requirements.txt
python main.py
```

## Core Game Features

The game is a 2D top-down map of cities, industrial facilities and a road network. The player builds roads, places stops, purchases vehicles, defines routes, and transports goods and passengers.

### Map and City Development

- **Grid-based map** — cities and industrial facilities sit on a grid. They can't be moved, but they can be connected by roads.
- **City growth** — cities expand over time, increasing in size and internal road network. Growth is influenced by the city's economy.
- **Roads** — built on empty tiles, or on forested tiles after clearing. Connecting cities and facilities is the main task.

### Vehicles and Routes

- **Vehicle types** — buses, trucks and trains, each suited to particular goods or to passengers, with different speeds, capacities and maintenance costs.
- **Stops and routes** — the player creates circular routes and vehicles travel them automatically. Bus stops pick up passengers.

### Economy and Time

- **Capital** — you start with a fixed amount; income comes from successful deliveries.
- **Costs** — roads, vehicles and maintenance all cost money. Run out and you go bankrupt: game over.
- **Time speed** — pause, normal, fast (2x) and very fast (4x).

## Subtasks

The optional subtasks the team took on, each worth 0.5 complexity:

**Forests** — trees appear on empty tiles, 1–4 per tile, and can spread over time. Roads can be built on forested tiles at a higher cost for clearing.

**Rivers and lakes** — water requires bridges to cross. At least three bridge types, each with different materials and speed limits.

**Garage** — vehicles return to the garage for maintenance, and older vehicles need it more often. Vehicles can be bought here, or sold once they're too old to run economically.

**City growth** — cities grow over time, especially where there's regular traffic in goods or passengers, expanding into adjacent tiles with new buildings and roads.

**Minimap** — the map scrolls, with a minimap for navigation.

**Continuous movement** — vehicles move smoothly between tiles rather than jumping, for more realistic animation.

**Map generation** — each map is generated procedurally, so no two sessions are alike.

## Project Structure

```
src/
  models/     vehicle, facility, route, stop, tile, grid, garage, company
  engine/     map generation, pathfinding, city growth, camera
  render/     map renderer, minimap
  ui/         HUD, start screen, fonts
tests/        unit tests, plus tests/frontend for game-loop and bankruptcy
main.py
```

## Tests

```bash
pytest
```

CI runs on every push (`.gitlab-ci.yml`): flake8 linting, then pytest with coverage and JUnit reports.

---

Inspired by [OpenTTD](https://www.openttd.org/) — see it [on Steam](https://store.steampowered.com/app/1536610/OpenTTD/).
