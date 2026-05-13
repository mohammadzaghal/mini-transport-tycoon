"""Tests for src/models/company.py"""
import pytest
from src.models.company import Company


class TestCompanyInit:
    def test_stores_name_and_money(self):
        c = Company("Acme", 5000)
        assert c.name == "Acme"
        assert c.money == 5000

    def test_default_totals_zero(self):
        c = Company("X", 0)
        assert c.total_income == 0
        assert c.total_expenses == 0

    def test_default_resources_zero(self):
        c = Company("X", 1000)
        assert c.fuel == 0.0
        assert c.iron_ore == 0.0
        assert c.alloy_ore == 0.0
        assert c.titanium_ore == 0.0


class TestCompanySpend:
    def test_spend_reduces_money(self):
        c = Company("X", 1000)
        c.spend(400)
        assert c.money == 600

    def test_spend_returns_true_on_success(self):
        c = Company("X", 1000)
        assert c.spend(500) is True

    def test_spend_records_expenses(self):
        c = Company("X", 1000)
        c.spend(300)
        c.spend(200)
        assert c.total_expenses == 500

    def test_spend_returns_false_when_overdrafting(self):
        c = Company("X", 100)
        result = c.spend(200)
        assert result is False

    def test_overspend_drives_balance_negative(self):
        c = Company("X", 100)
        c.spend(200)
        assert c.money == -100

    def test_overspend_records_full_expense(self):
        c = Company("X", 100)
        c.spend(999)
        assert c.total_expenses == 999

    def test_spend_exact_amount_succeeds(self):
        c = Company("X", 500)
        assert c.spend(500) is True
        assert c.money == 0

    def test_spend_zero(self):
        c = Company("X", 100)
        assert c.spend(0) is True
        assert c.money == 100


class TestCompanyEarn:
    def test_earn_increases_money(self):
        c = Company("X", 100)
        c.earn(200)
        assert c.money == 300

    def test_earn_records_income(self):
        c = Company("X", 0)
        c.earn(100)
        c.earn(50)
        assert c.total_income == 150

    def test_earn_zero(self):
        c = Company("X", 100)
        c.earn(0)
        assert c.money == 100
        assert c.total_income == 0


class TestCompanyBankruptcy:
    def test_not_bankrupt_with_positive_money(self):
        c = Company("X", 1)
        assert c.is_bankrupt is False

    def test_not_bankrupt_at_zero(self):
        c = Company("X", 0)
        assert c.is_bankrupt is False

    def test_bankrupt_when_negative(self):
        c = Company("X", 0)
        c.money = -1
        assert c.is_bankrupt is True

    def test_spend_below_zero_then_bankrupt(self):
        """Edge case: money becomes negative via direct mutation (game engine does this)."""
        c = Company("X", 50)
        c.money -= 100
        assert c.is_bankrupt is True

    def test_earn_recovers_from_negative(self):
        c = Company("X", 0)
        c.money = -500
        c.earn(1000)
        assert c.is_bankrupt is False
        assert c.money == 500
