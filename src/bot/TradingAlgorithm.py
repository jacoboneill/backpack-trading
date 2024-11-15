class TradingAlgorithm:
    def __init__(self, trading_account):
        self.stocks = [
            {
                "ticker": stock,
                "prev": None,
                "current": trading_account.portfolio[stock]["price"],
                "weight": None,
                "normalised_weight": None,
            }
            for stock in trading_account.portfolio
        ]

        self.portfolio = trading_account.portfolio
        self.budget = trading_account.budget

    def _calculateWeights(self, new_prices):
        new_prices = dict(new_prices)
        weighted_stocks = list()
        for stock in self.stocks:
            data = {
                "ticker": stock["ticker"],
                "prev": stock["current"],
                "normalised_weight": None,
            }

            if stock["ticker"] in new_prices:
                data["current"] = new_prices[stock["ticker"]]
            else:
                data["current"] = data["prev"]

            data["weight"] = (data["current"] - data["prev"]) / 2

            weighted_stocks.append(data)

        self.stocks = weighted_stocks

    def _getMaxMin(self):
        max = float("-inf")
        min = float("inf")
        for stock in self.stocks:
            if stock["weight"] > max:
                max = stock["weight"]
            if stock["weight"] < min:
                min = stock["weight"]

        return (max, min)

    def _normaliseWeights(self):
        max, min = self._getMaxMin()
        for stock in self.stocks:
            stock["normalised_weight"] = ((stock["weight"] - min) / (max - min)) + 1

    def _updateStocks(self, new_prices):
        self._calculateWeights(new_prices)
        self._normaliseWeights()
        self.portfolio.updateAllStocks(new_prices)

    def _cleanKnapsackValues(self, knapsack_stocks):
        portfolio = dict()
        for stock in knapsack_stocks:
            if stock in portfolio:
                portfolio[stock]["quantity"] += 1
            else:
                portfolio[stock] = {"quantity": 1}

        return portfolio

    def _unboundedKnapsackRecurs(self, budget, i):
        if i == 0:
            count = int(budget // self.stocks[0]["normalised_weight"])
            return (
                count * self.stocks[0]["current"],
                [self.stocks[0]["ticker"]] * count,
            )

        not_take_val, not_take_items = self._unboundedKnapsackRecurs(budget, i - 1)

        take_val = float("-inf")
        take_items = list()

        if self.stocks[i]["normalised_weight"] <= budget:
            take_val_recurs, take_items_recurs = self._unboundedKnapsackRecurs(
                budget - self.stocks[i]["normalised_weight"], i - 1
            )
            take_val = self.stocks[i]["current"] + take_val_recurs
            take_items = [self.stocks[i]["ticker"]] + take_items_recurs

            if take_val > not_take_val:
                return (take_val, take_items)
            else:
                return (not_take_val, not_take_items)

    def unboundedKnapsack(self, new_prices):
        self._updateStocks(new_prices)

        n = len(self.stocks)
        import json

        print(json.dumps(self.stocks, indent=1))
        value, items = self._unboundedKnapsackRecurs(n - 1, self.budget)
        return _cleanKnapsackValues(items)
