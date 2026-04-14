from __future__ import annotations

import random
from typing import Optional, List

import pygame

from src.config import (
    BOTTOM_BAR_HEIGHT,
    BRIDGE_ORE_COSTS,
    BRIDGE_VEHICLE_SUPPORT,
    FOREST_CLEAR_COST,
    GAME_SECONDS_PER_DAY,
    GARAGE_COST,
    MAINTENANCE_BASE_COST,
    MAINTENANCE_INTERVAL_DAYS,
    MAP_HEIGHT,
    MAP_WIDTH,
    PASSENGER_FARE,
    ROAD_COST,
    STARTING_MONEY,
    TILE_SIZE,
    TICK_MS,
    TRACK_COST,
    VEHICLE_DEFS,
    VEHICLE_LEVEL_DEFS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.engine.camera import Camera
from src.engine.city_growth import CityGrowthManager
from src.engine.map_generator import MapGenerator
from src.engine.pathfinding import find_road_path, find_track_path
from src.enums import BridgeType, CargoType, TimeSpeed, TileType, Tool, VehicleType
from src.models.company import Company
from src.models.garage import Garage
from src.models.grid import Grid
from src.models.route import Route
from src.models.stop import Stop
from src.models.vehicle import Vehicle
from src.render.map_renderer import MapRenderer
from src.render.minimap import Minimap
from src.ui.hud import HUD

TREE_GROWTH_INTERVAL = 60.0
FPS = 1000 // TICK_MS

_CITY_NAMES = frozenset({"Olympus Base", "Valles Station", "Arcadia Colony"})


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.fullscreen = False
        self.clock = pygame.time.Clock()

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.company = Company("Player Co.", STARTING_MONEY)
        self.company.iron_ore = 30
        self.company.alloy_ore = 10
        self.company.titanium_ore = 5
        self.time_speed = TimeSpeed.NORMAL
        self.tool = Tool.NONE
        self.status_message = (
            "Welcome! Build roads [R] or tracks [T], create routes, then buy and deploy vehicles."
        )

        self.game_time = 0.0
        self.tree_growth_timer = 0.0

        self.routes: List[Route] = []
        self._next_route_id = 1
        self._route_endpoint_a: Optional[tuple] = None

        self.garage: List[Vehicle] = []
        self.vehicles: List[Vehicle] = []
        self._pending_deploy_idx: Optional[int] = None
        self._deploy_endpoint_a: Optional[tuple] = None

        self.stops: List[Stop] = []
        self._next_stop_id = 1

        self.garages: List[Garage] = []

        self._garage_panel_tile: Optional[tuple] = None

        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE,
            view_width=WINDOW_WIDTH,
            view_height=WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
        )
        self.renderer = MapRenderer()
        self.minimap = Minimap()
        self._show_minimap = True
        self.hud = HUD()

        map_gen = MapGenerator()
        self.facilities, city_origins = map_gen.generate(self.grid)
        self.renderer.build_map_image(self.grid)
        self.minimap.build(self.grid)

        self.city_growth = CityGrowthManager()
        for city_name, sx, sy in city_origins:
            self.city_growth.register_city(city_name, sx, sy)

        self._city_has_water: dict = {name: False for name in _CITY_NAMES}

        self._rng = random.Random()
        self._hover_tile: Optional[tuple] = None

        self._drag_start_screen: Optional[tuple] = None
        self._drag_start_camera: Optional[tuple] = None
        self._dragging_map = False
        self._drag_threshold = 8

        self._bankrupt = False

    def tick(self, events: list) -> bool:
        dt_ms = self.clock.tick(FPS)
        real_dt = dt_ms / 1000.0

        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_left_press(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._on_left_release(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._on_mouse_move(event.pos, bool(event.buttons[0]))
            elif event.type == pygame.MOUSEWHEEL:
                mods = pygame.key.get_mods()
                scroll = event.y * 48
                if mods & pygame.KMOD_SHIFT:
                    self.camera.move(-scroll, 0)
                else:
                    self.camera.move(0, -scroll)
            elif event.type == pygame.KEYDOWN:
                self._on_key_down(event.key)

        self._handle_camera_input(real_dt)

        if self.time_speed != TimeSpeed.PAUSE and not self._bankrupt:
            sim_dt = real_dt * self.time_speed.value
            self.update(sim_dt)

        self.draw()
        pygame.display.flip()

        return not self._bankrupt

    def update(self, dt: float) -> None:
        self.game_time += dt

        for facility in self.facilities.values():
            facility.tick(dt)

        for vehicle in list(self.vehicles):
            completed = vehicle.update(dt)

            if vehicle.at_stop:
                tile = self.grid.get_tile(int(round(vehicle.x)), int(round(vehicle.y)))
                if tile is not None and ((tile.is_stop and tile.stop_ref is not None) or tile.is_entry_point):
                    self._handle_vehicle_at_stop(vehicle, tile)

            if completed:
                route = next((r for r in self.routes if r.id == vehicle.route_id), None)
                if route and route.profitable:
                    for ep in (route.endpoint_a, route.endpoint_b):
                        ep_tile = self.grid.get_tile(*ep)
                        if ep_tile and ep_tile.zone_name in _CITY_NAMES:
                            if self._city_has_water.get(ep_tile.zone_name, False):
                                self.city_growth.on_delivery(ep_tile.zone_name)

            vehicle.age_days += dt / GAME_SECONDS_PER_DAY
            vehicle.maintenance_timer += dt / GAME_SECONDS_PER_DAY
            if (
                vehicle.maintenance_timer >= vehicle.maintenance_due_days
                and not vehicle.needs_maintenance
            ):
                vehicle.needs_maintenance = True
                age_factor = max(1.0, vehicle.age_days / 30.0)
                cost = int(MAINTENANCE_BASE_COST * age_factor)
                self.company.spend(cost)
                vehicle.maintenance_timer = 0.0
                vehicle.maintenance_due_days = float(MAINTENANCE_INTERVAL_DAYS)
                vehicle.needs_maintenance = False
                self.status_message = (
                    "{} maintenance — paid ${}.".format(vehicle.name, cost)
                )

        self.city_growth.tick(self.grid, self.renderer, self.minimap)

        self.tree_growth_timer += dt
        if self.tree_growth_timer >= TREE_GROWTH_INTERVAL:
            self.tree_growth_timer -= TREE_GROWTH_INTERVAL
            self._update_trees()

        if self.company.is_bankrupt:
            self._bankrupt = True
            self.status_message = "BANKRUPT! Game over. Close the window to exit."

    def _handle_vehicle_at_stop(self, vehicle: Vehicle, tile) -> None:
        from src.config import CARGO_PRICE

        zone = tile.zone_name or (tile.stop_ref.zone_name if tile.stop_ref else "")

        if vehicle.vehicle_type == VehicleType.BUS:
            passengers = self._rng.randint(0, vehicle.capacity)
            if passengers > 0:
                income = passengers * PASSENGER_FARE
                self.company.earn(income)
                self.status_message = (
                    "{} picked up {} passengers at stop (+${}).".format(
                        vehicle.name, passengers, income
                    )
                )
            return

        if CargoType.FUEL in vehicle.cargo_on_board and vehicle.cargo_on_board[CargoType.FUEL] > 0:
            for nb in self.grid.neighbors4(tile.x, tile.y):
                if nb.is_garage:
                    fuel_amount = int(vehicle.cargo_on_board.pop(CargoType.FUEL, 0))
                    self.company.fuel += fuel_amount
                    self.status_message = (
                        "{} deposited {} FUEL at garage (total: {}). Click garage to upgrade!".format(
                            vehicle.name, fuel_amount, self.company.fuel
                        )
                    )
                    return

        if vehicle.total_cargo > 0 and zone in _CITY_NAMES:
            city_has_water = self._city_has_water.get(zone, False)
            for cargo_type, amount in vehicle.unload_all().items():
                if cargo_type == CargoType.IRON_ORE:
                    self.company.iron_ore += amount
                elif cargo_type == CargoType.ALLOY_ORE:
                    self.company.alloy_ore += amount
                elif cargo_type == CargoType.TITANIUM_ORE:
                    self.company.titanium_ore += amount
                elif cargo_type == CargoType.FUEL:
                    self.company.fuel += amount

                revenue = int(amount * CARGO_PRICE.get(cargo_type, 5))
                if revenue > 0:
                    self.company.earn(revenue)

                if cargo_type == CargoType.AQUATICS and not city_has_water:
                    self._city_has_water[zone] = True
                    city_has_water = True
                    self.city_growth.on_delivery(zone)
                    self.status_message = "{}  UNLOCKED — water connected! City can now grow.".format(zone)
                elif revenue > 0:
                    if city_has_water:
                        self.city_growth.on_delivery(zone)
                        self.status_message = "{} delivery +${} (city growing).".format(zone, revenue)
                    else:
                        self.status_message = "{} delivery +${} (connect H2O to unlock city growth).".format(zone, revenue)

        if zone and zone not in _CITY_NAMES:
            facility = self.facilities.get(zone)
            if facility is not None:
                for cargo_type in list(facility.produces.keys()):
                    available = facility.stock(cargo_type)
                    if available > 0:
                        space = vehicle.capacity - int(vehicle.total_cargo)
                        to_load = min(float(space), available)
                        if to_load > 0:
                            taken = facility.give(cargo_type, to_load)
                            vehicle.load(cargo_type, taken)

    def _update_trees(self) -> None:
        new_forests = []
        for tile in self.grid.iter_tiles():
            if self._rng.random() < 0.45:
                continue
            if tile.tile_type == TileType.FOREST:
                if tile.tree_count < 4 and self._rng.random() < 0.07:
                    tile.tree_count += 1
                for nb in self.grid.neighbors4(tile.x, tile.y):
                    if nb.tile_type == TileType.GRASS and self._rng.random() < 0.012:
                        new_forests.append(nb)
        for tile in new_forests:
            if tile.tile_type == TileType.GRASS:
                tile.tile_type = TileType.FOREST
                tile.tree_count = 1
                self.renderer.update_tile(tile.x, tile.y, tile)

    def draw(self) -> None:
        self.renderer.draw(
            self.screen, self.grid, self.camera,
            self.routes, self.vehicles, self._hover_tile, self.stops,
        )
        self._draw_scrollbars()

        if self._show_minimap:
            if self.minimap._dirty:
                self.minimap.build(self.grid)
            self.minimap.draw(self.screen, self.camera, self.vehicles, self.stops)

        self.hud.draw(
            self.screen,
            money=self.company.money,
            oil=self.company.fuel,
            iron_ore=self.company.iron_ore,
            alloy_ore=self.company.alloy_ore,
            titanium_ore=self.company.titanium_ore,
            game_time=self.game_time,
            time_speed=self.time_speed,
            tool=self.tool,
            status=self.status_message,
            garage=self.garage,
            vehicles=self.vehicles,
            stops=self.stops,
            routes=self.routes,
            garage_panel_tile=self._garage_panel_tile,
            garage_vehicles=self._get_garage_vehicles_at(self._garage_panel_tile),
        )

        if self._bankrupt:
            overlay = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((180, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont("segoeui", 48, bold=True)
            surf = font.render("BANKRUPT — GAME OVER", True, (255, 60, 60))
            self.screen.blit(
                surf,
                (
                    WINDOW_WIDTH // 2 - surf.get_width() // 2,
                    (WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT) // 2 - 30,
                ),
            )

    def _get_garage_vehicles_at(self, garage_tile: Optional[tuple]) -> List[Vehicle]:
        return list(self.garage) + list(self.vehicles)

    def _draw_scrollbars(self) -> None:
        bar_width = 10
        bar_x = WINDOW_WIDTH - bar_width
        bar_height = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT
        thumb_height = min(
            bar_height,
            int(bar_height * self.camera.view_height / self.camera.map_height_px),
        )
        thumb_y = int(
            (bar_height - thumb_height)
            * self.camera.y
            / max(1, self.camera.map_height_px - self.camera.view_height)
        )
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, 0, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, thumb_y, bar_width, thumb_height))
        bar_y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT - bar_width
        bar_width_h = WINDOW_WIDTH
        thumb_width = min(
            bar_width_h,
            int(bar_width_h * self.camera.view_width / self.camera.map_width_px),
        )
        thumb_x = int(
            (bar_width_h - thumb_width)
            * self.camera.x
            / max(1, self.camera.map_width_px - self.camera.view_width)
        )
        pygame.draw.rect(self.screen, (200, 200, 200), (0, bar_y, bar_width_h, bar_width))
        pygame.draw.rect(self.screen, (100, 100, 100), (thumb_x, bar_y, thumb_width, bar_width))

    def _on_left_press(self, pos: tuple) -> None:
        x, y = pos
        if self._is_in_map_view(x, y):
            self._drag_start_screen = pos
            self._drag_start_camera = (self.camera.x, self.camera.y)
            self._dragging_map = False

    def _on_mouse_move(self, pos: tuple, left_held: bool) -> None:
        x, y = pos
        self._update_hover_from_screen(x, y)

        if left_held and self._drag_start_screen is not None:
            sx, sy = self._drag_start_screen
            dx = x - sx
            dy = y - sy
            if abs(dx) >= self._drag_threshold or abs(dy) >= self._drag_threshold:
                self._dragging_map = True
            if self._dragging_map and self._drag_start_camera is not None:
                cam_sx, cam_sy = self._drag_start_camera
                self.camera.x = cam_sx - dx
                self.camera.y = cam_sy - dy
                self.camera.clamp()

        if not (left_held and self._dragging_map):
            grid_pos = self._screen_to_grid(x, y)
            if grid_pos is not None:
                gx, gy = grid_pos
                tile = self.grid.get_tile(gx, gy)
                if tile is not None:
                    parts = ["Tile ({},{}) {}".format(gx, gy, tile.tile_type.name)]
                    if tile.zone_name:
                        parts.append(tile.zone_name)
                    if tile.is_entry_point:
                        parts.append("ENTRY")
                    if tile.is_bank:
                        parts.append("BANK")
                    if tile.is_stop:
                        parts.append("STOP")
                    if tile.is_garage:
                        parts.append("GARAGE")
                    if tile.bridge_type is not None:
                        parts.append("BRIDGE:{}".format(tile.bridge_type.value))
                    if tile.is_city_road:
                        parts.append("CITY ROAD")
                    self.status_message = "  |  ".join(parts)

    def _on_left_release(self, pos: tuple) -> None:
        x, y = pos
        if self._dragging_map:
            self._clear_drag_state()
            return

        if self._show_minimap and self.minimap.handle_click(x, y, self.camera):
            self._clear_drag_state()
            return

        if self._garage_panel_tile is not None:
            garage_veh = self._get_garage_vehicles_at(self._garage_panel_tile)
            garage_action = self.hud.garage_panel_button_at(x, y, garage_veh)
            if garage_action is not None:
                self._handle_hud_action(garage_action)
                self._clear_drag_state()
                return
            if self.hud.is_in_garage_panel(x, y):
                self._clear_drag_state()
                return

        hud_action = self.hud.button_at(x, y, self.tool, self.garage, self.routes)
        if hud_action is not None:
            self._handle_hud_action(hud_action)
            self._clear_drag_state()
            return

        if not self._is_in_map_view(x, y):
            self._clear_drag_state()
            return

        grid_pos = self._screen_to_grid(x, y)
        if grid_pos is None:
            self._clear_drag_state()
            return

        gx, gy = grid_pos

        if self.tool == Tool.NONE:
            tile = self.grid.get_tile(gx, gy)
            if tile is not None and tile.is_garage:
                self._garage_panel_tile = (gx, gy) if self._garage_panel_tile != (gx, gy) else None
                self._clear_drag_state()
                return
            if self._garage_panel_tile is not None:
                self._garage_panel_tile = None

        if self.tool == Tool.ROAD:
            self._build_road(gx, gy)
        elif self.tool == Tool.TRACK:
            self._build_track(gx, gy)
        elif self.tool == Tool.ROUTE_P1:
            self._handle_route_click_p1(gx, gy)
        elif self.tool == Tool.ROUTE_P2:
            self._handle_route_click_p2(gx, gy)
        elif self.tool == Tool.DEPLOY_VEHICLE_P1:
            self._handle_deploy_click_p1(gx, gy)
        elif self.tool == Tool.DEPLOY_VEHICLE_P2:
            self._handle_deploy_click_p2(gx, gy)
        elif self.tool == Tool.BULLDOZE:
            self._bulldoze(gx, gy)
        elif self.tool == Tool.STOP:
            self._build_stop(gx, gy)
        elif self.tool == Tool.BRIDGE:
            self._build_bridge(gx, gy)
        elif self.tool == Tool.GARAGE:
            self._build_garage(gx, gy)

        self._clear_drag_state()

    def _on_key_down(self, key: int) -> None:
        if key == pygame.K_1:
            self.time_speed = TimeSpeed.PAUSE
        elif key == pygame.K_2:
            self.time_speed = TimeSpeed.NORMAL
        elif key == pygame.K_3:
            self.time_speed = TimeSpeed.FAST
        elif key == pygame.K_4:
            self.time_speed = TimeSpeed.VERY_FAST
        elif key == pygame.K_ESCAPE:
            self._cancel_tool()
            self._garage_panel_tile = None
        elif key == pygame.K_r:
            self._set_tool(Tool.ROAD, "Road mode — click tiles to lay road [${}/tile].".format(ROAD_COST))
        elif key == pygame.K_t:
            self._set_tool(Tool.TRACK, "Track mode — click tiles to lay train track [${}/tile].".format(TRACK_COST))
        elif key == pygame.K_b:
            self._set_tool(Tool.BULLDOZE, "Bulldoze — click a route road to remove the route, click again to remove the tile.")
        elif key == pygame.K_s:
            self._set_tool(Tool.STOP, "Stop mode — click a road or track tile to place a stop.")
        elif key == pygame.K_g:
            self._set_tool(
                Tool.GARAGE,
                "Garage mode — click an empty tile to build a garage (${}).".format(GARAGE_COST),
            )
        elif key == pygame.K_k:
            self._set_tool(Tool.BRIDGE, "Bridge mode — select bridge type below, then click a water tile.")
        elif key == pygame.K_m:
            self._show_minimap = not self._show_minimap
            self.status_message = "Minimap {}.".format("on" if self._show_minimap else "off")
        elif key == pygame.K_F11:
            self._toggle_fullscreen()

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

    def _handle_camera_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        step = int(500 * dt)
        use_wasd = self.tool == Tool.NONE
        if (use_wasd and keys[pygame.K_a]) or keys[pygame.K_LEFT]:
            self.camera.move(-step, 0)
        if (use_wasd and keys[pygame.K_d]) or keys[pygame.K_RIGHT]:
            self.camera.move(step, 0)
        if (use_wasd and keys[pygame.K_w]) or keys[pygame.K_UP]:
            self.camera.move(0, -step)
        if (use_wasd and keys[pygame.K_s]) or keys[pygame.K_DOWN]:
            self.camera.move(0, step)

    def _handle_hud_action(self, action: str) -> None:
        if action == "road":
            if self.tool == Tool.ROAD:
                self._cancel_tool()
            else:
                self._set_tool(Tool.ROAD, "Road mode — click tiles to lay road (${}/tile).".format(ROAD_COST))
        elif action == "track":
            if self.tool == Tool.TRACK:
                self._cancel_tool()
            else:
                self._set_tool(Tool.TRACK, "Track mode — click tiles to lay train track (${}/tile).".format(TRACK_COST))
        elif action == "vehicles":
            if self.tool in {Tool.VEHICLES, Tool.DEPLOY_VEHICLE_P1, Tool.DEPLOY_VEHICLE_P2}:
                self._cancel_tool()
            else:
                self._set_tool(Tool.VEHICLES, "Purchase a vehicle or deploy one from your fleet.")
        elif action == "route":
            if self.tool in {Tool.ROUTE_P1, Tool.ROUTE_P2}:
                self._cancel_tool()
            else:
                self._set_tool(Tool.ROUTE_P1, "Route — click first endpoint (entry point or stop).")
        elif action == "stop":
            if self.tool == Tool.STOP:
                self._cancel_tool()
            else:
                self._set_tool(Tool.STOP, "Stop mode — click a road or track tile to place a stop.")
        elif action == "bridge":
            if self.tool == Tool.BRIDGE:
                self._cancel_tool()
            else:
                self._set_tool(Tool.BRIDGE, "Bridge mode — select level below, then click a WATER tile.")
        elif action == "bulldoze":
            if self.tool == Tool.BULLDOZE:
                self._cancel_tool()
            else:
                self._set_tool(Tool.BULLDOZE, "Bulldoze — 1st click on route road removes route; 2nd click removes tile.")
        elif action == "garage":
            if self.tool == Tool.GARAGE:
                self._cancel_tool()
            else:
                self._set_tool(Tool.GARAGE, "Garage mode — click an empty tile (${}).".format(GARAGE_COST))
        elif action == "bridge_wooden":
            self.hud.selected_bridge_type = BridgeType.WOODEN
            self.status_message = "L1 Basic bridge — costs 10 Iron Ore/tile · Hauler only. Click a water tile."
        elif action == "bridge_stone":
            self.hud.selected_bridge_type = BridgeType.STONE
            self.status_message = "L2 Reinforced bridge — costs 10 Alloy Ore/tile · Hauler + Rover. Click a water tile."
        elif action == "bridge_steel":
            self.hud.selected_bridge_type = BridgeType.STEEL
            self.status_message = "L3 Magnetic bridge — costs 10 Titanium Ore/tile · all vehicles. Click a water tile."
        elif action == "speed_pause":
            self.time_speed = TimeSpeed.PAUSE
        elif action == "speed_1":
            self.time_speed = TimeSpeed.NORMAL
        elif action == "speed_2":
            self.time_speed = TimeSpeed.FAST
        elif action == "speed_4":
            self.time_speed = TimeSpeed.VERY_FAST
        elif action.startswith("buy_vehicle_"):
            idx = int(action.split("_")[-1])
            self._buy_vehicle(idx)
        elif action.startswith("deploy_type_"):
            type_idx = int(action.split("_")[-1])
            self._select_garage_vehicle_by_type(type_idx)
        elif action.startswith("remove_route_"):
            route_id = int(action.split("_")[-1])
            route = next((r for r in self.routes if r.id == route_id), None)
            if route:
                self._dissolve_route(route)
        elif action.startswith("upgrade_vehicle_"):
            v_idx = int(action.split("_")[-1])
            self._upgrade_vehicle(v_idx)
        elif action.startswith("sell_vehicle_"):
            v_idx = int(action.split("_")[-1])
            self._sell_garage_vehicle(v_idx)
        elif action == "close_garage_panel":
            self._garage_panel_tile = None

    def _set_tool(self, tool: Tool, msg: str) -> None:
        self.tool = tool
        self.status_message = msg

    def _cancel_tool(self, message: str = "Ready.") -> None:
        self.tool = Tool.NONE
        self._route_endpoint_a = None
        self._deploy_endpoint_a = None
        self._pending_deploy_idx = None
        self.status_message = message

    def _build_road(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.is_city_road:
            self.status_message = "City roads cannot be modified."
            return
        if not self.grid.is_road_buildable(x, y):
            self.status_message = "Roads can only be built on grass or forest tiles."
            return
        cost = ROAD_COST + (FOREST_CLEAR_COST if tile.tile_type == TileType.FOREST else 0)
        if not self.company.spend(cost):
            self.status_message = "Not enough credits (need ${}).".format(cost)
            return
        tile.tile_type = TileType.ROAD
        tile.tree_count = 0
        self.renderer.update_tile(x, y, tile)
        self.minimap.update_tile(x, y, tile)
        self.status_message = "Road built at ({},{}) — ${}.".format(x, y, cost)

    def _build_track(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.is_entry_point:
            self.status_message = "Cannot build track on an entry point."
            return
        if not self.grid.is_track_buildable(x, y):
            self.status_message = "Tracks can only be built on grass, forest, or road tiles."
            return
        cost = TRACK_COST + (FOREST_CLEAR_COST if tile.tile_type == TileType.FOREST else 0)
        if not self.company.spend(cost):
            self.status_message = "Not enough credits (need ${}).".format(cost)
            return
        tile.tile_type = TileType.TRACK
        tile.is_route_road = False
        tile.tree_count = 0
        self.renderer.update_tile(x, y, tile)
        self.minimap.update_tile(x, y, tile)
        self.status_message = "Track built at ({},{}) — ${}.".format(x, y, cost)

    def _build_stop(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type not in {TileType.ROAD, TileType.TRACK}:
            self.status_message = "Stops can only be placed on road or track tiles."
            return
        if tile.is_stop:
            self.status_message = "There is already a stop here."
            return

        zone_name = tile.zone_name
        if not zone_name:
            for nb in self.grid.neighbors4(x, y):
                if nb.zone_name:
                    zone_name = nb.zone_name
                    break

        stop = Stop(id=self._next_stop_id, x=x, y=y, zone_name=zone_name)
        self._next_stop_id += 1
        tile.is_stop = True
        tile.stop_ref = stop
        self.stops.append(stop)
        self.renderer.update_tile(x, y, tile)
        self.minimap.update_tile(x, y, tile)
        self.status_message = "Stop #{} placed at ({},{}) — serves {}.".format(
            stop.id, x, y, zone_name or "general"
        )

    def _build_bridge(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type != TileType.WATER:
            self.status_message = "Bridges can only be built on water tiles."
            return
        if tile.bridge_type is not None:
            self.status_message = "There is already a bridge here."
            return

        bridge_type = self.hud.selected_bridge_type
        ore_cargo, ore_cost = BRIDGE_ORE_COSTS[bridge_type]
        reserve_attr = ore_cargo.name.lower()
        current_ore = getattr(self.company, reserve_attr)
        if current_ore < ore_cost:
            self.status_message = "Need {} {} to build this bridge (have {}).".format(
                ore_cost, ore_cargo.value, current_ore
            )
            return

        setattr(self.company, reserve_attr, current_ore - ore_cost)
        tile.bridge_type = bridge_type
        self.renderer.update_tile(x, y, tile)
        self.minimap.update_tile(x, y, tile)
        lv = {
            "Wooden": "L1 (Hauler only)",
            "Stone":  "L2 (Hauler+Rover)",
            "Steel":  "L3 (all vehicles)",
        }
        self.status_message = "{} bridge at ({},{}) — cost: {} {}.".format(
            lv.get(bridge_type.value, bridge_type.value), x, y, ore_cost, ore_cargo.value
        )

    def _build_garage(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type not in {TileType.GRASS, TileType.FOREST}:
            self.status_message = "Garages can only be built on grass or forest tiles."
            return
        if tile.is_garage:
            self.status_message = "There is already a garage here."
            return
        if not self.company.spend(GARAGE_COST):
            self.status_message = "Not enough credits for a garage (need ${}).".format(GARAGE_COST)
            return

        garage = Garage(x=x, y=y)
        tile.tile_type = TileType.GRASS
        tile.is_garage = True
        tile.garage_ref = garage
        tile.tree_count = 0
        self.garages.append(garage)
        self.renderer.update_tile(x, y, tile)
        self.minimap.update_tile(x, y, tile)
        self.status_message = "Garage built at ({},{}) — ${}.  Click it to upgrade vehicles.".format(
            x, y, GARAGE_COST
        )

    def _bulldoze(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return

        if tile.is_city_road and tile.is_entry_point:
            self.status_message = "Entry points cannot be removed."
            return

        if tile.is_stop:
            self.stops = [s for s in self.stops if not (s.x == x and s.y == y)]
            tile.is_stop = False
            tile.stop_ref = None
            self.renderer.update_tile(x, y, tile)
            self.minimap.update_tile(x, y, tile)
            self.status_message = "Stop removed at ({},{}).".format(x, y)
            return

        if tile.bridge_type is not None:
            tile.bridge_type = None
            tile.tile_type = TileType.WATER
            self.renderer.update_tile(x, y, tile)
            self.minimap.update_tile(x, y, tile)
            self.status_message = "Bridge removed at ({},{}) — water restored.".format(x, y)
            return

        if tile.is_garage:
            self.garages = [g for g in self.garages if not (g.x == x and g.y == y)]
            tile.is_garage = False
            tile.garage_ref = None
            self.renderer.update_tile(x, y, tile)
            self.minimap.update_tile(x, y, tile)
            if self._garage_panel_tile == (x, y):
                self._garage_panel_tile = None
            self.status_message = "Garage removed at ({},{}).".format(x, y)
            return

        if tile.tile_type in {TileType.ROAD, TileType.TRACK} and not tile.is_entry_point:
            route = next(
                (r for r in self.routes if (x, y) in r.path), None
            )
            if route is not None:
                self._dissolve_route(route)
                return
            tile.tile_type = TileType.GRASS
            tile.is_route_road = False
            self.renderer.update_tile(x, y, tile)
            self.minimap.update_tile(x, y, tile)
            self.status_message = "Tile removed at ({},{}).".format(x, y)
        else:
            self.status_message = "Nothing to bulldoze here."

    def _handle_route_click_p1(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not (tile.is_entry_point or tile.is_stop):
            self.status_message = "First endpoint must be an entry point (◆) or stop (S)."
            return
        self._route_endpoint_a = (x, y)
        self.tool = Tool.ROUTE_P2
        self.status_message = "First: {} at ({},{}). Now click the second endpoint.".format(
            tile.zone_name or "stop", x, y
        )

    def _handle_route_click_p2(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not (tile.is_entry_point or tile.is_stop):
            self.status_message = "Second endpoint must be an entry point (◆) or stop (S)."
            return
        if (x, y) == self._route_endpoint_a:
            self.status_message = "Endpoints must be different tiles."
            return

        ep_a = self._route_endpoint_a
        ep_b = (x, y)

        outbound = find_road_path(self.grid, ep_a, ep_b)
        path_type = "road"
        if not outbound:
            outbound = find_track_path(self.grid, ep_a, ep_b)
            path_type = "track"

        if not outbound:
            self._cancel_tool("No road or track connecting those endpoints — build a path first.")
            return

        inbound = list(reversed(outbound))
        loop_path = outbound + inbound[1:]

        tile_a = self.grid.get_tile(*ep_a)
        tile_b = self.grid.get_tile(*ep_b)
        a_is_city = tile_a.zone_name in _CITY_NAMES
        b_is_city = tile_b.zone_name in _CITY_NAMES
        profitable = a_is_city != b_is_city

        route = Route(
            id=self._next_route_id,
            name="Route {}".format(self._next_route_id),
            endpoint_a=ep_a,
            endpoint_b=ep_b,
            path=loop_path,
            profitable=profitable,
            path_type=path_type,
        )
        self._next_route_id += 1
        self.routes.append(route)

        for rx, ry in outbound:
            t = self.grid.get_tile(rx, ry)
            if t is not None:
                t.is_route_road = True
                self.renderer.update_tile(rx, ry, t)
                self.minimap.update_tile(rx, ry, t)

        vtype = "train" if path_type == "track" else "bus/truck"
        income_note = "Earns income." if profitable else "No income — connect facility→city."
        self.status_message = "{} ({}) created ({} tiles). {} Deploy a {}!".format(
            route.name, path_type, len(outbound), income_note, vtype
        )
        self._cancel_tool()

    def _handle_deploy_click_p1(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not (tile.is_entry_point or tile.is_stop):
            self.status_message = "First endpoint must be an entry point (◆) or stop (S)."
            return
        self._deploy_endpoint_a = (x, y)
        self.tool = Tool.DEPLOY_VEHICLE_P2
        self.status_message = "First endpoint: ({},{}). Now click the second endpoint.".format(x, y)

    def _handle_deploy_click_p2(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not (tile.is_entry_point or tile.is_stop):
            self.status_message = "Second endpoint must be an entry point (◆) or stop (S)."
            return
        if (x, y) == self._deploy_endpoint_a:
            self.status_message = "Endpoints must be different tiles."
            return

        ep_a = self._deploy_endpoint_a
        ep_b = (x, y)
        endpoints = {ep_a, ep_b}

        matching = [r for r in self.routes if {r.endpoint_a, r.endpoint_b} == endpoints]
        if not matching:
            self._cancel_tool("No route connects those endpoints. Create a route first.")
            return

        route = matching[0]

        if self._pending_deploy_idx is None:
            self._cancel_tool()
            return

        vehicle = self.garage[self._pending_deploy_idx]

       if vehicle.vehicle_type == VehicleType.TRAIN and route.path_type != "track":
            self._cancel_tool("Trains can only run on track routes. Build a track route first.")
            return
        if vehicle.vehicle_type in {VehicleType.BUS, VehicleType.TRUCK} and route.path_type == "track":
            self._cancel_tool("Buses and trucks cannot run on track routes.")
            return

        vtype_key = {VehicleType.BUS: "bus", VehicleType.TRUCK: "truck", VehicleType.TRAIN: "train"}[vehicle.vehicle_type]
        for rx, ry in route.path:
            t = self.grid.get_tile(rx, ry)
            if t is not None and t.bridge_type is not None:
                support = BRIDGE_VEHICLE_SUPPORT.get(t.bridge_type, {})
                if not support.get(vtype_key, True):
                    bridge_name = {BridgeType.WOODEN: "L1 Basic", BridgeType.STONE: "L2 Reinforced", BridgeType.STEEL: "L3 Magnetic"}[t.bridge_type]
                    self._cancel_tool(
                        "{} cannot cross {} bridge on this route. Build a higher bridge level.".format(
                            vehicle.name, bridge_name))
                    return

        distance = max(1, len(route.path) // 2)
        vehicle.reward_distance = distance
        vehicle.revenue_per_leg = self._calc_revenue(distance, vehicle.capacity)
        vehicle.path = route.path
        vehicle.route_id = route.id
        vehicle.initialize_position()

        self.vehicles.append(vehicle)
        self.garage.pop(self._pending_deploy_idx)
        self._pending_deploy_idx = None
        self._deploy_endpoint_a = None

        self.status_message = "{} deployed on {}.".format(vehicle.name, route.name)
        self._cancel_tool()

    def _dissolve_route(self, route: Route) -> None:
        for rx, ry in route.path:
            t = self.grid.get_tile(rx, ry)
            if t is not None:
                t.is_route_road = False
                self.renderer.update_tile(rx, ry, t)
                self.minimap.update_tile(rx, ry, t)

        staying = [v for v in self.vehicles if v.route_id != route.id]
        returning = [v for v in self.vehicles if v.route_id == route.id]
        for v in returning:
            v.path = []
            v.route_id = -1
            v.current_index = 0
            self.garage.append(v)
        self.vehicles = staying
        self.routes = [r for r in self.routes if r.id != route.id]
        self.status_message = "{} removed. {} vehicle(s) returned to garage. Roads intact.".format(
            route.name, len(returning)
        )

    def _buy_vehicle(self, vdef_index: int) -> None:
        vdef = VEHICLE_DEFS[vdef_index]
        if not self.company.spend(vdef["cost"]):
            self.status_message = "Not enough credits (need ${}).".format(vdef["cost"])
            return
        vehicle_number = len(self.garage) + len(self.vehicles) + 1
        vtype = vdef["vehicle_type"]
        spd = vdef["speed"]
        cap = vdef["capacity"]
        vehicle = Vehicle(
            name="{} {}".format(vdef["name"], vehicle_number),
            vehicle_type=vtype,
            path=[],
            speed_tiles_per_second=spd,
            capacity=cap,
            base_speed=spd,
            base_capacity=cap,
            level=1,
            color=vdef["color"],
            route_id=-1,
            vdef_name=vdef["name"],
        )
        self.garage.append(vehicle)
        self.status_message = "{} purchased for ${}. Open Fleet to deploy it.".format(
            vdef["name"], vdef["cost"]
        )

    def _select_garage_vehicle_by_type(self, type_idx: int) -> None:
        vdef_name = VEHICLE_DEFS[type_idx]["name"]
        for i, v in enumerate(self.garage):
            if v.vdef_name == vdef_name:
                self._pending_deploy_idx = i
                self._set_tool(
                    Tool.DEPLOY_VEHICLE_P1,
                    "Deploying {} — click first route endpoint.".format(vdef_name),
                )
                return
        self.status_message = "No {} in garage.".format(vdef_name)

    def _upgrade_vehicle(self, v_idx: int) -> None:
        all_vehicles = list(self.garage) + list(self.vehicles)
        if v_idx < 0 or v_idx >= len(all_vehicles):
            return
        vehicle = all_vehicles[v_idx]
        if vehicle.level >= 3:
            self.status_message = "{} is already at max level.".format(vehicle.name)
            return
        next_level = vehicle.level + 1
        level_def = VEHICLE_LEVEL_DEFS.get(vehicle.vehicle_type, {}).get(next_level)
        if level_def is None:
            return
        oil_cost = level_def["oil"]
        if self.company.fuel < oil_cost:
            self.status_message = "Need {} FUEL to upgrade {} to L{} (have {}).".format(
                oil_cost, vehicle.name, next_level, self.company.fuel
            )
            return

        self.company.fuel -= oil_cost
        vehicle.level = next_level
        vehicle.speed_tiles_per_second = vehicle.base_speed * (level_def["speed_mult"] ** (next_level - 1))
        vehicle.capacity = int(vehicle.base_capacity * (level_def["cap_mult"] ** (next_level - 1)))
        self.status_message = "{} upgraded to Level {}! Speed: {:.1f}, Capacity: {}.".format(
            vehicle.name, next_level, vehicle.speed_tiles_per_second, vehicle.capacity
        )

    def _sell_garage_vehicle(self, v_idx: int) -> None:
        all_vehicles = list(self.garage) + list(self.vehicles)
        if v_idx < 0 or v_idx >= len(all_vehicles):
            return
        vehicle = all_vehicles[v_idx]
        vdef = next((d for d in VEHICLE_DEFS if d["name"] == vehicle.vdef_name), None)
        sell_price = int(vdef["cost"] * 0.5) if vdef else 200
        if vehicle in self.garage:
            self.garage.remove(vehicle)
        elif vehicle in self.vehicles:
            self.vehicles.remove(vehicle)
        self.company.earn(sell_price)
        self.status_message = "{} sold for ${}.".format(vehicle.name, sell_price)

    def _calc_revenue(self, distance: int, capacity: int) -> int:
        speed_bonus = self.time_speed.value if self.time_speed.value > 0 else 1
        return int(18 * distance + capacity * 6 + speed_bonus * 5)

    def _is_in_map_view(self, x: int, y: int) -> bool:
        return 0 <= y < WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT

    def _screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[tuple]:
        world_x, world_y = self.camera.screen_to_world(screen_x, screen_y)
        grid_x = world_x // TILE_SIZE
        grid_y = world_y // TILE_SIZE
        if not self.grid.in_bounds(grid_x, grid_y):
            return None
        return grid_x, grid_y

    def _update_hover_from_screen(self, screen_x: int, screen_y: int) -> None:
        if not self._is_in_map_view(screen_x, screen_y):
            self._hover_tile = None
            return
        self._hover_tile = self._screen_to_grid(screen_x, screen_y)

    def _clear_drag_state(self) -> None:
        self._drag_start_screen = None
        self._drag_start_camera = None
        self._dragging_map = False