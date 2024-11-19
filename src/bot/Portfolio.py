from __future__ import annotations
from Stock import Stock


class PortfolioStock(Stock):
    def __init__(self, ticker: str, price: float, quantity: int) -> None:
        if quantity < 1:
            raise ValueError(f"quantity must be above one, {quantity} was given.")

        super().__init__(ticker, price)
        self.quantity: int = quantity


class StockNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)


class Portfolio:
    def __init__(self) -> None:
        self.stocks: dict[str, PortfolioStock] = {}
        self.value: float = 0

        self.value = self._calculateValue()

    def _calculateValue(self) -> float:
        value = 0
        for stock in self.stocks.values():
            value += stock.price * stock.quantity

        return value

    def addStock(self, stock: Stock, quantity: int = 1) -> None:
        if not isinstance(quantity, int):
            raise ValueError(
                f"quantity must be of type int, {type(quantity)} was given"
            )

        if quantity < 1:
            raise ValueError(
                f"quantity must be above or equal to 1, {quantity} was given."
            )

        if stock.ticker in self.stocks:
            quantity: int = self.stocks[stock.ticker].quantity + quantity

        new_stock: PortfolioStock = PortfolioStock(
            stock.ticker, stock.price, quantity=quantity
        )

        self.stocks[new_stock.ticker] = new_stock

    def removeStock(self, stock: Stock, quantity: int = -1) -> None:
        if not isinstance(quantity, int):
            raise ValueError(f"quantity must be of type int, {quantity} was given")

        if quantity > 0:
            raise ValueError(f"quantity must be below 0, {quantity} was given.")

        if stock.ticker not in self.stocks:
            raise StockNotFoundError(
                f"Request to remove {stock.ticker} was not completed. Was not found in Portfolio."
            )

        new_quantity = self.stocks[stock.ticker].quantity + quantity
        if new_quantity < 0:
            raise StockNotFoundError(
                f"Request to remove {stock.ticker} {-quantity} times was not completed. {self.stocks[stock.ticker].quantity} stocks left in Portfolio."
            )

        if new_quantity >= 1:
            self.stocks[stock.ticker].quantity += quantity
        elif new_quantity == 0:
            self.stocks.pop(stock.ticker)

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

    def __repr__(self):
        return "\n".join(
            [
                f"- {stock.ticker} x {stock.quantity} @ ${stock.price}"
                for stock in self.stocks.values()
            ]
        )
