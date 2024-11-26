from typing import Union
from stock import Stock
from portfolio import Portfolio


class TradingAlgorithmStock(Stock):
    def __init__(
        self, ticker: str, old_price: float, new_price: float, raw_weight: float
    ) -> None:
        self.ticker: str = ticker
        self.old_price: float = old_price
        self.new_price: float = new_price
        self.raw_weight: float = raw_weight
        self.normalised_weight: Union[None, float] = None
        self.scaled_price: Union[None, float] = None


class TradingAlgorithm:
    def __init__(
        self, old_stocks: dict[str, Stock], new_stocks: dict[str, Stock]
    ) -> None:
        self.stocks: list = []
        for ticker in old_stocks:
            self.addStock(
                old_stocks[ticker],
                new_stocks[ticker] if ticker in new_stocks else old_stocks[ticker],
            )

        for stock in self.stocks:
            stock.normalised_weight = self._calculateNormalisedWeight(stock)
            stock.scaled_price = self._scalePrice(stock)

    def addStock(self, old_stock: Stock, new_stock: Stock) -> None:
        if old_stock.ticker != new_stock.ticker:
            raise ValueError(
                f"Tickers must match: {old_stock.ticker} != {new_stock.ticker}"
            )

        raw_weight = self._calculateRawWeight(old_stock.price, new_stock.price)
        self.stocks.append(
            TradingAlgorithmStock(old_stock.ticker, old_stock.price, new_stock.price, raw_weight)
        )

    def _calculateRawWeight(self, old_price, new_price) -> float:
        return (new_price - old_price) / 2

    def _calculateRawWeightMaxMin(self) -> tuple[float, float]:
        generator = [stock.raw_weight for stock in self.stocks]
        return (max(generator), min(generator))

    def _calculateNormalisedWeight(self, stock: TradingAlgorithmStock) -> float:
        max_value, min_value = self._calculateRawWeightMaxMin()
        return ((stock.raw_weight - min_value) / (max_value - min_value)) + 1

    def _scalePrice(self, stock: TradingAlgorithmStock) -> float:
        if not hasattr(self, "scale"):
            max_digits: float = max(
                len(str(stock.new_price).split(".")[1]) for stock in self.stocks
            )
            self.scale: int = pow(10, max_digits)
        return int(stock.new_price * self.scale)

    def getOptimalPortfolio(self, budget: float) -> Portfolio:
        scaled_budget: int = int(budget * self.scale)

        dp = [0] * (scaled_budget + 1)  # TODO find out type of dp
        chosen = [-1] * (scaled_budget + 1)  # TODO find out type of chosen

        for i in range(len(self.stocks)):
            for j in range(self.stocks[i].scaled_price, scaled_budget + 1):
                take = (
                    self.stocks[i].normalised_weight
                    + dp[j - self.stocks[i].scaled_price]
                )  # TODO find out type of take
                if take > dp[j]:
                    dp[j] = take
                    chosen[j] = i

        optimal_portfolio = Portfolio()
        remaining_scaled_budget = scaled_budget
        while remaining_scaled_budget >= 0 and chosen[remaining_scaled_budget] != -1:
            stock_index = chosen[
                remaining_scaled_budget
            ]  # TODO find out type of stock_index
            stock: TradingAlgorithmStock = self.stocks[stock_index]
            optimal_portfolio.addStock(Stock(stock.ticker, stock.new_price))
            remaining_scaled_budget -= self.stocks[stock_index].scaled_price

        return optimal_portfolio
