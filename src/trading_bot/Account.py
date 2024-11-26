from portfolio import Portfolio, PortfolioStock
from stock import Stock


class InsufficientFundsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self, self.message)


class Account:
    def __init__(self, initial_balance: float, budget_percentage: float):
        if initial_balance < 0:
            raise ValueError(
                f"initial_balance must be above 0, {initial_balance} was given."
            )

        if budget_percentage < 0 or budget_percentage > 1:
            raise ValueError(
                f"budget percentage must be between 0 and one, {budget_percentage} was given."
            )

        self.initial_balance: float = initial_balance
        self.balance: float = initial_balance
        self.budget_percentage: float = budget_percentage
        self.budget: float = self._calculateBudget()
        self.portfolio: Portfolio = Portfolio()

    def _calculateBudget(self) -> float:
        return self.balance * self.budget_percentage

    def updateStockHistory(self, new_stocks: Portfolio) -> tuple[Portfolio, Portfolio]:
        if not hasattr(self, "new_stocks"):
            self.old_stocks: Portfolio = new_stocks
        else:
            self.old_stocks: Portfolio = self.new_stocks

        self.new_stocks = new_stocks

        return (self.old_stocks, self.new_stocks)

    def rebalanceAccount(self, portfolio_template: Portfolio) -> None:
        portfolio: dict[str, PortfolioStock] = self.portfolio.stocks
        template: dict[str, PortfolioStock] = portfolio_template.stocks
        buy_queue: list = []
        sell_queue: list = []

        for ticker, new_stock in template.items():
            if ticker not in portfolio:
                quantity: int = new_stock.quantity
                stock: Stock = Stock(ticker, new_stock.price)
            else:
                quantity: int = template[ticker].quantity - portfolio[ticker].quantity
                stock: Stock = Stock(ticker, new_stock.price)

            if quantity > 0:
                buy_queue.append((stock, quantity))
            if quantity < 0:
                sell_queue.append((stock, quantity))

        for ticker, old_stock in portfolio.items():
            if ticker not in template:
                quantity: int = -old_stock.quantity
                stock: Stock = Stock(ticker, old_stock.price)
                sell_queue.append((stock, quantity))

        for stock, quantity in sell_queue:
            self._sellStocks(stock, quantity)

        for stock, quantity in buy_queue:
            self._buyStocks(stock, quantity)

        self.budget = self._calculateBudget()
        self.portfolio.value = self.portfolio._calculateValue()

    def _buyStocks(self, stock: Stock, quantity: int = 1):
        if not isinstance(quantity, int):
            raise ValueError(f"quantity must be of type int, {type(quantity)} given.")

        if quantity < 1:
            raise ValueError(
                f"quantity must be above or equal to 1, {quantity} was given."
            )

        request_price = stock.price * quantity
        if self.balance + request_price < 0:
            raise InsufficientFundsError(
                f"Unable to complete transaction: {stock.ticker} x {quantity}. Insufficient funds."
            )

        self.balance -= request_price
        self.portfolio.addStock(stock, quantity=quantity)

    def _sellStocks(self, stock: Stock, quantity: int = -1) -> None:
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
