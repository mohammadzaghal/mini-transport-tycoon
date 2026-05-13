from dataclasses import dataclass


@dataclass
class Company:
    """Tracks the player's finances and resource inventory.

    Attributes:
        name: Display name of the company.
        money: Current cash balance in game currency.
        total_income: Cumulative earnings over the entire session.
        total_expenses: Cumulative spending over the entire session.
        fuel: Current fuel stock held by the company (in units).
        iron_ore: Current iron ore stock (in units).
        alloy_ore: Current alloy ore stock (in units).
        titanium_ore: Current titanium ore stock (in units).
    """

    name: str
    money: int
    total_income: int = 0
    total_expenses: int = 0
    fuel: float = 0.0
    iron_ore: float = 0.0
    alloy_ore: float = 0.0
    titanium_ore: float = 0.0

    def spend(self, amount: int) -> bool:
        """Deduct an amount from the company's cash balance.

        Args:
            amount: The positive integer amount to deduct.

        Returns:
            True if the balance remains non-negative after the deduction,
            False if the company has gone into debt.
        """
        self.money -= amount
        self.total_expenses += amount
        return self.money >= 0

    def earn(self, amount: int) -> None:
        """Add an amount to the company's cash balance.

        Args:
            amount: The positive integer amount to add.
        """
        self.money += amount
        self.total_income += amount

    @property
    def is_bankrupt(self) -> bool:
        """True when the company's cash balance has dropped below zero."""
        return self.money < 0
