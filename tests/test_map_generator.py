from __future__ import annotations

from src.config import MAP_HEIGHT, MAP_WIDTH
from src.engine.map_generator import MapGenerator
from src.enums import TileType
from src.models.grid import Grid


def _run_generator(seed: int) -> tuple[Grid, dict, list]:
    grid = Grid(MAP_WIDTH, MAP_HEIGHT)
    gen = MapGenerator(seed=seed)
    facilities, city_origins = gen.generate(grid)
    return grid, facilities, city_origins


class TestDeterminism:
    def test_same_seed_produces_identical_maps(self):
        g1, f1, c1 = _run_generator(seed=42)
        g2, f2, c2 = _run_generator(seed=42)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                assert g1.get_tile(x, y).tile_type == g2.get_tile(x, y).tile_type
        assert c1 == c2
        assert set(f1.keys()) == set(f2.keys())

    def test_different_seeds_produce_different_maps(self):
        g1, _, _ = _run_generator(seed=1)
        g2, _, _ = _run_generator(seed=2)
        diff_count = sum(
            1
            for y in range(MAP_HEIGHT)
            for x in range(MAP_WIDTH)
            if g1.get_tile(x, y).tile_type != g2.get_tile(x, y).tile_type
        )
        assert diff_count > 0


class TestPlacement:
    def test_all_three_cities_placed(self):
        _, _, city_origins = _run_generator(seed=7)
        names = {name for name, _, _ in city_origins}
        assert names == {"Olympus Base", "Valles Station", "Arcadia Colony"}

    def test_all_seven_facilities_placed(self):
        _, facilities, _ = _run_generator(seed=7)
        expected = {
            "North Mine", "South Mine", "Fuel Rig",
            "Aqua Dome N", "Aqua Dome E", "Aqua Dome S",
            "Crystal Lab",
        }
        assert set(facilities.keys()) == expected

    def test_generator_creates_water_tiles(self):
        grid, _, _ = _run_generator(seed=7)
        water = [t for t in grid.iter_tiles() if t.tile_type == TileType.WATER]
        assert len(water) > 0

    def test_each_city_has_entry_point(self):
        grid, _, city_origins = _run_generator(seed=7)
        for _, sx, sy in city_origins:
            entry = grid.get_tile(sx + 2, sy + 3)
            assert entry is not None
            assert entry.is_entry_point is True

    def test_seed_is_stored_on_generator(self):
        gen = MapGenerator(seed=12345)
        assert gen.seed == 12345

    def test_no_seed_produces_valid_seed(self):
        gen = MapGenerator()
        assert isinstance(gen.seed, int)
        assert gen.seed >= 0