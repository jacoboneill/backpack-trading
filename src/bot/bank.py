from account import Account


class Bank:
    def __init__(self):
        self.accounts: list[Account] = []

    def addAccount(self, initial_balance: float, budget_percentage: float):
        self.accounts.append(Account(initial_balance, budget_percentage))

    def __repr__(self):
        reprs: list[str] = []
        for account in self.accounts:
            initial_balance: float = account.initial_balance
            balance: float = account.balance
            budget: float = account.budget
            portfolio_value: float = account.portfolio.value
            profit_and_loss: float = (
                (balance + portfolio_value) - initial_balance
            ) / initial_balance

            reprs.append(
                f"Account:\n\t- Initial Balance: ${initial_balance:.2f}\n\t- Balance        : ${balance:.2f}\n\t- Budget         : ${budget:.2f}\n\t- Portfolio      : ${portfolio_value:.2f}\n\t- Profit / Loss  : {profit_and_loss}%\n-----------------------------------------------"
            )

        return "\n".join(reprs)
