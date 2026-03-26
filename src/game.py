from __future__ import annotations

import random
from typing import Optional, List

import pygame

from src.config import (
    BOTTOM_BAR_HEIGHT,
    FOREST_CLEAR_COST,
    MAP_HEIGHT,
    MAP_WIDTH,
    ROAD_COST,
    STARTING_MONEY,
    TILE_SIZE,
    TICK_MS,
    VEHICLE_DEFS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.engine.camera import Camera
from src.engine.map_generator import MapGenerator
from src.engine.pathfinding import find_road_path
from src.enums import CargoType, TimeSpeed, TileType, Tool
from src.models.company import Company
from src.models.grid import Grid
from src.models.route import Route
from src.models.vehicle import Vehicle
from src.render.map_renderer import MapRenderer
from src.ui.hud import HUD

TREE_GROWTH_INTERVAL = 60.0

FPS = 1000 // TICK_MS

_CITY_NAMES = frozenset({"Greenfield", "Riverside", "Southport"})


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Transport Tycoon")
        self.fullscreen = False
        self.clock = pygame.time.Clock()

        self.grid = Grid(MAP_WIDTH, MAP_HEIGHT)
        self.company = Company("Player Co.", STARTING_MONEY)
        self.time_speed = TimeSpeed.NORMAL
        self.tool = Tool.NONE
        self.status_message = "Welcome! Build roads between entry points, create routes, then buy and deploy vehicles."

        self.game_time = 0.0
        self.tree_growth_timer = 0.0

        self.routes: List[Route] = []
        self._next_route_id = 1
        self._route_endpoint_a: Optional[tuple] = None

        
        self.garage: List[Vehicle] = []
        self.vehicles: List[Vehicle] = []
        self._pending_deploy_idx: Optional[int] = None   
        self._deploy_endpoint_a: Optional[tuple] = None

        self.camera = Camera(
            map_width_px=MAP_WIDTH * TILE_SIZE,
            map_height_px=MAP_HEIGHT * TILE_SIZE,
            view_width=WINDOW_WIDTH,
            view_height=WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT,
        )
        self.renderer = MapRenderer()
        self.hud = HUD()

        MapGenerator(seed=7).generate(self.grid)
        self.renderer.build_map_image(self.grid)

        self._rng = random.Random()
        self._hover_tile: Optional[tuple] = None

        self._drag_start_screen: Optional[tuple] = None
        self._drag_start_camera: Optional[tuple] = None
        self._dragging_map = False
        self._drag_threshold = 8

  
    def run(self) -> None:
        running = True
        while running:
            dt_ms = self.clock.tick(FPS)
            real_dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._on_left_press(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._on_left_release(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._on_mouse_move(event.pos, bool(event.buttons[0]))
                elif event.type == pygame.MOUSEWHEEL:
                    # Scroll vertically; hold Shift for horizontal
                    mods = pygame.key.get_mods()
                    scroll = event.y * 48   # pixels per wheel notch
                    if mods & pygame.KMOD_SHIFT:
                        self.camera.move(-scroll, 0)
                    else:
                        self.camera.move(0, -scroll)
                elif event.type == pygame.KEYDOWN:
                    self._on_key_down(event.key)

            self._handle_camera_input(real_dt)

            if self.time_speed != TimeSpeed.PAUSE:
                sim_dt = real_dt * self.time_speed.value
                self.update(sim_dt)

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def update(self, dt: float) -> None:
        self.game_time += dt

        for vehicle in self.vehicles:
            completed = vehicle.update(dt)
            if completed:
                route = next((r for r in self.routes if r.id == vehicle.route_id), None)
                if route and route.profitable:
                    revenue = vehicle.revenue_per_leg
                    self.company.earn(revenue)
                    self.status_message = "{} delivered goods and earned ${}.".format(vehicle.name, revenue)

        self.tree_growth_timer += dt
        if self.tree_growth_timer >= TREE_GROWTH_INTERVAL:
            self.tree_growth_timer -= TREE_GROWTH_INTERVAL
            self._update_trees()













    def draw(self) -> None:
        self.renderer.draw(
            self.screen, self.grid, self.camera,
            self.routes, self.vehicles, self._hover_tile,
        )
        self._draw_scrollbars()
        self.hud.draw(
            self.screen,
            money=self.company.money,
            game_time=self.game_time,
            time_speed=self.time_speed,
            tool=self.tool,
            status=self.status_message,
            garage=self.garage,
            vehicles=self.vehicles,
        )

    def _draw_scrollbars(self) -> None:
        bar_width = 10
        bar_x = WINDOW_WIDTH - bar_width
        bar_height = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT
        thumb_height = min(bar_height, int(bar_height * self.camera.view_height / self.camera.map_height_px))
        thumb_y = int((bar_height - thumb_height) * self.camera.y / max(1, self.camera.map_height_px - self.camera.view_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, 0, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, thumb_y, bar_width, thumb_height))
        bar_y = WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT - bar_width
        bar_width_h = WINDOW_WIDTH
        thumb_width = min(bar_width_h, int(bar_width_h * self.camera.view_width / self.camera.map_width_px))
        thumb_x = int((bar_width_h - thumb_width) * self.camera.x / max(1, self.camera.map_width_px - self.camera.view_width))
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
                    self.status_message = "  |  ".join(parts)

    def _on_left_release(self, pos: tuple) -> None:
        x, y = pos
        if self._dragging_map:
            self._clear_drag_state()
            return

        hud_action = self.hud.button_at(x, y, self.tool, self.garage)
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
        if self.tool == Tool.ROAD:
            self._build_road(gx, gy)
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
        elif key == pygame.K_r:
            self._set_tool(Tool.ROAD, "Road mode — click tiles to lay road.")
        elif key == pygame.K_b:
            self._set_tool(Tool.BULLDOZE, "Bulldoze mode — click roads to remove them.")
        elif key == pygame.K_F11:
            self._toggle_fullscreen()

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

    def _handle_camera_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        step = int(500 * dt)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera.move(-step, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera.move(step, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera.move(0, -step)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera.move(0, step)


    def _handle_hud_action(self, action: str) -> None:
        if action == "road":
            if self.tool == Tool.ROAD:
                self._cancel_tool()
            else:
                self._set_tool(Tool.ROAD, "Road mode — click map tiles to lay road (${} each).".format(ROAD_COST))
        elif action == "vehicles":
            if self.tool in {Tool.VEHICLES, Tool.DEPLOY_VEHICLE_P1, Tool.DEPLOY_VEHICLE_P2}:
                self._cancel_tool()
            else:
                self._set_tool(Tool.VEHICLES, "Purchase a vehicle or deploy one from your fleet.")
        elif action == "route":
            if self.tool in {Tool.ROUTE_P1, Tool.ROUTE_P2}:
                self._cancel_tool()
            else:
                self._set_tool(Tool.ROUTE_P1, "Route mode — click a city or facility entry point for the first endpoint.")
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

    def _set_tool(self, tool: Tool, msg: str) -> None:
        self.tool = tool
        self.status_message = msg

    def _cancel_tool(self, message: str = "Ready.") -> None:
        self.tool = Tool.NONE
        self._route_endpoint_a = None
        self._deploy_endpoint_a = None
        self._pending_deploy_idx = None
        self.status_message = message


# for bulldoze we should make it more user friendly

    def _build_road(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if not self.grid.is_road_buildable(x, y):
            self.status_message = "Can only build roads on grass or forest tiles."
            return
        cost = ROAD_COST + (FOREST_CLEAR_COST if tile.tile_type == TileType.FOREST else 0)
        if not self.company.spend(cost):
            self.status_message = "Not enough credits to build road (need ${}).".format(cost)
            return
        tile.tile_type = TileType.ROAD
        tile.tree_count = 0
        self.renderer.update_tile(x, y, tile)
        self.status_message = "Road built at ({},{}) for ${}.".format(x, y, cost)



    def _bulldoze(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        if tile.tile_type == TileType.ROAD and not tile.is_entry_point:
            for route in self.routes:
                if (x, y) in route.path:
                    self._dissolve_route(route)
                    return
            tile.tile_type = TileType.GRASS
            tile.is_route_road = False
            self.renderer.update_tile(x, y, tile)
            self.status_message = "Road removed at ({},{}).".format(x, y)

    def _handle_route_click_p1(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not tile.is_entry_point:
            self.status_message = "First endpoint must be a city or facility entry point (marked ENTRY)."
            return
        self._route_endpoint_a = (x, y)  #store the first endpoint coordinates for use in step 2
        self.tool = Tool.ROUTE_P2         
        self.status_message = "First endpoint: {} at ({},{}). Now click the second entry point.".format(
            tile.zone_name, x, y)

    def _handle_route_click_p2(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not tile.is_entry_point:
            self.status_message = "Second endpoint must be a city or facility entry point (marked ENTRY)."
            return
        if (x, y) == self._route_endpoint_a:
            self.status_message = "Endpoints must be different tiles."
            return 

        ep_a = self._route_endpoint_a  
        ep_b = (x, y)

        outbound = find_road_path(self.grid, ep_a, ep_b)
        if not outbound:
            self._cancel_tool("ERROR: No road connecting those entry points — build roads between them first.")
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
        )

        self._next_route_id += 1
        self.routes.append(route)

        for rx, ry in outbound:
            t = self.grid.get_tile(rx, ry)
            if t is not None:
                t.is_route_road = True
                self.renderer.update_tile(rx, ry, t)

        income_note = "Earns income (facility→city)." if profitable else "No income — connect a facility to a city for revenue."
        self.status_message = "{} created ({} tiles). {} Deploy a vehicle to use it!".format(
            route.name, len(outbound), income_note)
        self._cancel_tool()

    def _handle_deploy_click_p1(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not tile.is_entry_point:
            self.status_message = "First endpoint must be a city or facility entry point (marked ENTRY)."
            return
        self._deploy_endpoint_a = (x, y)
        self.tool = Tool.DEPLOY_VEHICLE_P2
        self.status_message = "First endpoint: {} at ({},{}). Now click the second entry point of the route.".format(
            tile.zone_name, x, y)

    def _handle_deploy_click_p2(self, x: int, y: int) -> None:
        tile = self.grid.get_tile(x, y)
        if tile is None or not tile.is_entry_point:
            self.status_message = "Second endpoint must be a city or facility entry point (marked ENTRY)."
            return
        if (x, y) == self._deploy_endpoint_a:
            self.status_message = "Endpoints must be different tiles."
            return

        ep_a = self._deploy_endpoint_a
        ep_b = (x, y)
        endpoints = {ep_a, ep_b}

        matching = [r for r in self.routes if {r.endpoint_a, r.endpoint_b} == endpoints]
        if not matching:
            self._cancel_tool("No route connects those two entry points. Select endpoints of an existing route.")
            return

        route = matching[0]

        if self._pending_deploy_idx is None:
            self._cancel_tool()
            return

        vehicle = self.garage[self._pending_deploy_idx]
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
                if t.tile_type == TileType.ROAD and not t.is_entry_point:
                    t.tile_type = TileType.GRASS
                self.renderer.update_tile(rx, ry, t)

        staying = [v for v in self.vehicles if v.route_id != route.id]
        returning = [v for v in self.vehicles if v.route_id == route.id]
        for v in returning:
            v.path = []
            v.route_id = -1
            v.current_index = 0
            self.garage.append(v)
        self.vehicles = staying

        self.routes = [r for r in self.routes if r.id != route.id]
        self.status_message = "{} dissolved. {} vehicle(s) returned to garage.".format(
            route.name, len(returning))

    def _buy_vehicle(self, vdef_index: int) -> None:
        vdef = VEHICLE_DEFS[vdef_index]  
        if not self.company.spend(vdef["cost"]):
            self.status_message = "Not enough credits (need ${}).".format(vdef["cost"])
            return

        vehicle_number = len(self.garage) + len(self.vehicles) + 1
        vehicle = Vehicle(
            name="{} {}".format(vdef["name"], vehicle_number),
            cargo_type=CargoType.PASSENGERS,
            path=[],
            speed_tiles_per_second=vdef["speed"],
            capacity=vdef["capacity"],
            color=vdef["color"],
            route_id=-1,
            vdef_name=vdef["name"],
        )
        self.garage.append(vehicle)
        self.status_message = "{} purchased for ${}. Open Fleet to deploy it.".format(
            vdef["name"], vdef["cost"])

    def _select_garage_vehicle_by_type(self, type_idx: int) -> None:
        vdef_name = VEHICLE_DEFS[type_idx]["name"]
        for i, v in enumerate(self.garage):
            if v.vdef_name == vdef_name:
                self._pending_deploy_idx = i
                self._set_tool(
                    Tool.DEPLOY_VEHICLE_P1,
                    "Deploying {} — click the first route endpoint.".format(vdef_name)
                )
                return
        self.status_message = "No {} in garage.".format(vdef_name)

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