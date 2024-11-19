from Portfolio import Portfolio
from Stock import Stock


class InsufficientFundsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self, self.message)


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

    def updateAccount(self, new_portfolio: Portfolio):
        new_stocks = new_portfolio.stocks

        buy_queue = list()
        sell_queue = list()

        for ticker, old_stock in self.portfolio.stocks.items():
            if ticker in new_stocks:
                new_stock = new_stocks[old_stock.ticker]
                quantity = new_stock.quantity - old_stock.quantity
            else:
                quantity = 0 - old_stock.quantity

            if quantity > 0:
                buy_queue.append((new_stock, quantity))
            if quantity < 0:
                sell_queue.append((old_stock, quantity))

        for stock, quantity in sell_queue:
            self.sellStock(stock, quantity)

        for stock, quantity in buy_queue:
            self.buyStock(stock, quantity)

        self.budget = self._calculateBudget()
        self.portfolio.value = self.portfolio._calculateValue()

    def buyStock(self, stock: Stock, quantity: int = 1):
        if not isinstance(quantity, int):
            raise ValueError(f"quantity must be of type int, {type(quantity)} given.")

        if quantity < 1:
            raise ValueError(
                f"quantity must be above or equal to 1, {quantity} was given."
            )

        request_price = self.portfolio.stocks[stock.ticker].price * quantity
        if self.balance + request_price < 0:
            raise InsufficientFundsError(
                f"Unable to complete transaction: {stock.ticker} x {quantity}. Insufficient funds."
            )

        self.balance -= request_price
        self.portfolio.addStock(stock, quantity=quantity)

    def sellStock(self, stock: Stock, quantity: int = -1) -> None:
        if not isinstance(quantity, int):
            raise ValueError(f"quantity must be of type int, {type(quantity)} given.")

        if quantity >= 0:
            raise ValueError(f"quantity must be below 0, {quantity} was given.")

        request_price = self.portfolio.stocks[stock.ticker].price * (-quantity)

        self.balance += request_price
        self.portfolio.removeStock(stock, quantity=quantity)

    def __repr__(self):
        portfolio_items = "\n".join(
            f"\t\t{item}" for item in repr(self.portfolio).split("\n")
        )
        return f"""Account:\n\
        Balance  : ${round(self.balance, 2)}\n\
        Budget   : ${round(self.budget, 2)}\n\
        Portfolio: ${round(self.portfolio.value, 2)}\n{portfolio_items}"""
