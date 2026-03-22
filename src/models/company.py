from dataclasses import dataclass

@dataclass
class Company:
    name: str
    money: int
    total_income: int = 0
    total_expenses: int = 0

    def spend(self, amount: int) -> bool:
        if amount > self.money:
            return False
        self.money -= amount
        self.total_expenses += amount
        return True

    def earn(self, amount: int) -> None:
        self.money += amount
        self.total_income += amount

    @property
    def is_bankrupt(self) -> bool:
        return self.money < 0
