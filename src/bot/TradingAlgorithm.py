from __future__ import annotations
from typing import Union


class Stock:
    def __init__(self, ticker: str, price: float) -> None:
        self.ticker: str = ticker
        self.price: float = price

    def __repr__(self) -> dict[str, Union[str, float]]:
        return repr(self.__dict__)


class PortfolioStock(Stock):
    def __init__(self, ticker: str, price: float, quantity: int = 1) -> None:
        super().__init__(ticker, price)
        self.quantity: int = quantity

    def __repr__(self) -> dict[str, Union[str, float, int]]:
        return repr(self.__dict__)


class TradingAlgorithmStock:
    def __init__(self, ticker: str, price: float) -> None:
        self.ticker: str = ticker
        self.current_price: float = price
        self.previous_price: Union[float, None] = None
        self.raw_weight: Union[float, None] = None
        self.normalised_weight: Union[float, None] = None
        self.scaled_price: Union[float, None] = None

    def __repr__(self) -> dict[str, Union[str, float, None]]:
        return repr(self.__dict__)


class StockNotFoundError(Exception):
    def __init__(self, message) -> None:
        self.message = message
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
        if stock.ticker in self.stocks:
            quantity: int = self.stocks[stock.ticker].quantity + quantity
        else:
            quantity: int = quantity

        self.stocks[stock.ticker] = PortfolioStock(
            stock.ticker, stock.price, quantity=quantity
        )

    def removeStock(self, stock: Stock, quantity: int = -1) -> None:
        old_stock_quantity = self.stocks[stock.ticker].quantity

        if stock.ticker in self.stocks:
            if old_stock_quantity + quantity >= 1:
                old_stock_quantity -= quantity
            elif old_stock_quantity + quantity == 0:
                self.stocks.pop(stock.ticker)
            else:
                raise StockNotFoundError(
                    f"Stock with ticker: {stock.ticker} was removed too many times."
                )
        else:
            raise StockNotFoundError(
                f"Stock with ticker: {stock.ticker} not found in portfolio. Could not remove."
            )

    def updateStock(self, new_stock: Stock) -> None:
        if new_stock.ticker not in self.stocks:
            raise StockNotFoundError(
                f"Unable to update stock: {new_stock.ticker} until added."
            )

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
        return f"Value: {self.value}\n" + "\n".join(
            [
                f"- {stock.ticker} x {stock.quantity} @ ${stock.price}"
                for stock in self.stocks.values()
            ]
        )


class TradingAccount:
    def __init__(self, portfolio: Portfolio, budget: float) -> None:
        self.portfolio = portfolio
        self.budget = budget


class TradingAlgorithm:
    def __init__(self, trading_account) -> None:
        self.stocks = [
            TradingAlgorithmStock(stock.ticker, stock.price)
            for stock in trading_account.portfolio.stocks.values()
        ]

        self.portfolio = trading_account.portfolio
        self.budget = trading_account.budget

    def _generateWeights(self, new_stocks: dict[str, Stock]) -> tuple[float, float]:
        for stock in self.stocks:
            stock.previous_price = stock.current_price

            if stock.ticker in new_stocks:
                stock.current_price = new_stocks[stock.ticker].price

            stock.raw_weight = (stock.current_price - stock.previous_price) / 2

    def _normaliseWeights(self) -> None:
        maxi: float = max(stock.raw_weight for stock in self.stocks)
        mini: float = min(stock.raw_weight for stock in self.stocks)

        for stock in self.stocks:
            stock.normalised_weight = ((stock.raw_weight - mini) / (maxi - mini)) + 1

    def _scalePrices(self) -> None:
        max_digits: float = max(
            len(str(stock.current_price).split(".")[1]) for stock in self.stocks
        )
        self.scale: int = pow(10, max_digits)

        self.scaled_budget: float = self.budget * self.scale

        for stock in self.stocks:
            stock.scaled_price = int(stock.current_price * self.scale)

    def _unboundedKnapsack(self) -> Portfolio:
        dp = [0] * (self.scaled_budget + 1)
        chosen = [-1] * (self.scaled_budget + 1)

        for i in range(len(self.stocks)):
            for j in range(self.stocks[i].scaled_price, self.scaled_budget + 1):
                take = (
                    self.stocks[i].normalised_weight
                    + dp[j - self.stocks[i].scaled_price]
                )
                if take > dp[j]:
                    dp[j] = take
                    chosen[j] = i

        bought_stocks = []
        remaining_scaled_budget = self.scaled_budget
        while remaining_scaled_budget >= 0 and chosen[remaining_scaled_budget] != -1:
            stock_index = chosen[remaining_scaled_budget]
            bought_stocks.append(self.stocks[stock_index])
            remaining_scaled_budget -= self.stocks[stock_index].scaled_price

        new_portfolio = Portfolio(
            Stock(stock.ticker, stock.current_price) for stock in bought_stocks
        )
        return new_portfolio

    def run(self, new_stocks: dict[str, Stock]):
        self.portfolio.updateStocks(new_stocks)
        self._generateWeights(new_stocks)
        self._normaliseWeights()
        self._scalePrices()

        optimal_portfolio = self._unboundedKnapsack()
        self.portfolio._updatePortfolio(optimal_portfolio)


if __name__ == "__main__":
    account: TradingAccount = TradingAccount(
        Portfolio([Stock("ENB", 41.075), Stock("WMT", 83.18)]), 10_000
    )
    new_stocks: dict[str, Stock] = {
        "ENB": Stock("ENB", 41.44),
        "WMT": Stock("WMT", 84.29),
    }

    print(account.portfolio)
    trading_algorithm: TradingAlgorithm = TradingAlgorithm(account)
    trading_algorithm.run(new_stocks)
    print()
    print(trading_algorithm.portfolio)
