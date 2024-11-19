from Portfolio import Portfolio


class Account:
    def __init__(
        self, initial_balance: float, budget_percentage: float, portfolio: Portfolio
    ):
        if initial_balance < 0:
            raise ValueError(
                f"initial_balance must be above 0, {initial_balance} was given."
            )

        if budget_percentage < 0 or budget_percentage > 1:
            raise ValueError(
                f"budget percentage must be between 0 and one, {budget_percentage} was given."
            )

        self.balance: float = initial_balance
        self.budget_percentage: float = budget_percentage
        self.budget: float = self._calculateBudget()
        self.portfolio: Portfolio = portfolio

    def _calculateBudget(self) -> float:
        return self.balance * self.budget_percentage

    def __repr__(self):
        portfolio_items = "\n".join(
            f"\t\t{item}" for item in repr(self.portfolio).split("\n")
        )
        return f"""Account:\n\
        Balance  : ${self.balance}\n\
        Budget   : ${self.budget}\n\
        Portfolio: ${self.portfolio.value}\n{portfolio_items}"""
