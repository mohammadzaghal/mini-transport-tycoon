from __future__ import annotations

import pygame
import pytest

from src.config import GARAGE_COST, ROAD_COST, TILE_SIZE, VEHICLE_DEFS
from src.enums import TileType, Tool
from src.models.company import Company


pytestmark = pytest.mark.slow


class TestCompanySpendAlwaysDeducts:
    def test_spend_within_budget_returns_true(self):
        c = Company("Test", 100)
        assert c.spend(60) is True
        assert c.money == 40
        assert c.is_bankrupt is False

    def test_spend_exactly_balance_returns_true(self):
        c = Company("Test", 100)
        assert c.spend(100) is True
        assert c.money == 0
        assert c.is_bankrupt is False

    def test_overspend_still_deducts_and_returns_false(self):
        c = Company("Test", 100)
        assert c.spend(150) is False
        assert c.money == -50
        assert c.is_bankrupt is True

    def test_overspend_records_total_expenses(self):
        c = Company("Test", 100)
        c.spend(150)
        assert c.total_expenses == 150

    def test_repeated_overspends_keep_compounding_debt(self):
        c = Company("Test", 100)
        c.spend(150)
        c.spend(20)
        assert c.money == -70
        assert c.is_bankrupt is True


def _click(x: int, y: int) -> list[pygame.event.Event]:
    return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (x, y)}),
            pygame.event.Event(pygame.MOUSEBUTTONUP,   {"button": 1, "pos": (x, y)})]


def _grass_in_view(game):
    for t in game.grid.iter_tiles():
        if t.tile_type != TileType.GRASS or t.is_city_road or t.is_entry_point:
            continue
        sx = t.x * TILE_SIZE - game.camera.x + TILE_SIZE // 2
        sy = t.y * TILE_SIZE - game.camera.y + TILE_SIZE // 2
        if 0 <= sx < 1280 and 0 <= sy < 600:
            return t.x, t.y, sx, sy
    raise AssertionError("no visible grass tile")


class TestInGameBankruptcy:
    def test_paving_road_with_no_money_still_paves_and_goes_negative(self, seeded_game):
        g = seeded_game
        g.company.money = ROAD_COST - 10
        gx, gy, sx, sy = _grass_in_view(g)
        g.tool = Tool.ROAD
        g.tick(_click(sx, sy))
        assert g.grid.get_tile(gx, gy).tile_type == TileType.ROAD
        assert g.company.money < 0
        assert g.company.is_bankrupt is True

    def test_buying_a_vehicle_below_zero_triggers_bankruptcy(self, seeded_game):
        g = seeded_game
        cheapest = min(v["cost"] for v in VEHICLE_DEFS)
        g.company.money = cheapest - 1
        cheapest_idx = next(i for i, v in enumerate(VEHICLE_DEFS)
                            if v["cost"] == cheapest)
        before_count = len(g.garage)
        g._buy_vehicle(cheapest_idx)
        assert len(g.garage) == before_count + 1
        assert g.company.money == -1
        assert g.company.is_bankrupt is True

    def test_garage_purchase_can_overdraft_too(self, seeded_game):
        g = seeded_game
        g.company.money = GARAGE_COST - 100
        gx, gy, sx, sy = _grass_in_view(g)
        g.tool = Tool.GARAGE
        before = len(g.garages)
        g.tick(_click(sx, sy))
        assert len(g.garages) == before + 1
        assert g.company.money == -100
        assert g.company.is_bankrupt is True

    def test_tick_returns_false_when_bankrupt(self, seeded_game):
        g = seeded_game
        g.company.money = -1
        g.tick([])
        assert g.tick([]) is False
        assert "BANKRUPT" in g.status_message.upper()
