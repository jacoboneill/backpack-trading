from __future__ import annotations
from Stock import Stock


class PortfolioStock(Stock):
    def __init__(self, ticker: str, price: float, quantity: int) -> None:
        super().__init__(ticker, price)
        self.quantity: int = quantity


class StockNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)


class Portfolio:
    def __init__(self, stocks: list[Stock]) -> None:
        self.stocks: dict = {}

        for stock in stocks:
            self.addStock(stock)

        self.value: float = self._calculateValue()

    def _calculateValue(self) -> float:
        value = 0
        for stock in self.stocks.values():
            value += stock.price * stock.quantity

        return value

    def addStock(self, stock: Stock, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError(
                f"Quantity must be above or equal to 1, {quantity} was given."
            )

        if not isinstance(quantity, int):
            raise ValueError(f"Quantity must be of type int, {quantity} was given")

        if stock.ticker in self.stocks:
            quantity: int = self.stocks[stock.ticker].quantity + quantity

        self.stocks[stock.ticker] = PortfolioStock(
            stock.ticker, stock.price, quantity=quantity
        )

    def removeStock(self, stock: Stock, quantity: int = -1) -> None:
        if quantity > 0:
            raise ValueError(f"Quantity must be below 0, {quantity} was given.")

        if not isinstance(quantity, int):
            raise ValueError(f"Quantity must be of type int, {quantity} was given")

        new_quantity = self.stocks[stock.ticker].quantity + quantity

        if stock.ticker in self.stocks:
            if new_quantity >= 1:
                self.stocks[stock.ticker].quantity += quantity
            elif new_quantity == 0:
                self.stocks.pop(stock.ticker)
            else:
                raise StockNotFoundError(
                    f"Request to remove {stock.ticker} {-quantity} times was not completed. {self.stocks[stock.ticker].quantity} stocks left in Portfolio."
                )
        else:
            raise StockNotFoundError(
                f"Request to remove {stock.ticker} was not completed. Was not found in Portfolio."
            )

    def updateStock(self, new_stock: Stock) -> None:
        if new_stock.ticker not in self.stocks:
            self.addStock(new_stock)
        else:
            self.stocks[new_stock.ticker] = PortfolioStock(
                new_stock.ticker,
                new_stock.price,
                quantity=self.stocks[new_stock.ticker].quantity,
            )

    def updateStocks(self, new_stocks: dict[str, Stock]) -> None:
        for ticker, stock in new_stocks.items():
            if ticker not in self.stocks:
                self.addStock(stock)
            else:
                self.updateStock(stock)

    def _updatePortfolio(self, new_portfolio: Portfolio) -> None:
        new_stocks = new_portfolio.stocks

        for ticker, old_stock in dict(self.stocks).items():
            if ticker in new_stocks:
                new_stock = new_stocks[old_stock.ticker]
                quantity = new_stock.quantity - old_stock.quantity
            else:
                quantity = 0 - old_stock.quantity

            if quantity > 0:
                self.addStock(new_stock, quantity=quantity)
            if quantity < 0:
                self.removeStock(old_stock, quantity=quantity)

        self.value = self._calculateValue()

    def __repr__(self):
        return "\n".join(
            [
                f"- {stock.ticker} x {stock.quantity} @ ${stock.price}"
                for stock in self.stocks.values()
            ]
        )
