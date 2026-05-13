from dataclasses import dataclass


@dataclass
class Company:
    name: str
    money: int
    total_income: int = 0
    total_expenses: int = 0
    fuel: float = 0.0
    iron_ore: float = 0.0
    alloy_ore: float = 0.0
    titanium_ore: float = 0.0

    def spend(self, amount: int) -> bool:
        self.money -= amount
        self.total_expenses += amount
        return self.money >= 0

    def earn(self, amount: int) -> None:
        self.money += amount
        self.total_income += amount

    @property
    def is_bankrupt(self) -> bool:
        return self.money < 0
