from Portfolio import Portfolio
from Stock import Stock
from Account import Account
from typing import Union


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


class TradingAlgorithm:
    def __init__(self, trading_account) -> None:
        self.stocks = [
            TradingAlgorithmStock(stock.ticker, stock.price)
            for stock in trading_account.portfolio.stocks.values()
        ]

        self.account = trading_account
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

        self.scaled_budget: int = int(self.budget * self.scale)

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
        self.portfolio._updatePortfolio(
            optimal_portfolio
        )  # TODO Update to self.account.updatePortfolio and update account balances


if __name__ == "__main__":
    portfolio: Portfolio = Portfolio([Stock("ENB", 41.075), Stock("WMT", 83.18)])
    account: Account = Account(10_000, 0.1, portfolio)
    new_stocks: dict[str, Stock] = {
        "ENB": Stock("ENB", 41.44),
        "WMT": Stock("WMT", 84.29),
    }

    print(account)
    trading_algorithm: TradingAlgorithm = TradingAlgorithm(account)
    trading_algorithm.run(new_stocks)
    print()
    print(trading_algorithm.account)
