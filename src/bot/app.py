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
        normalised_weights_stocks = list()
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

            normalised_weights_stocks.append(data)

        self.stocks = normalised_weights_stocks

    def _getMaxMin(self):
        max = 0
        min = 0
        for stock in self.stocks:
            if stock["weight"] > max:
                max = stock["weight"]
            if stock["weight"] < min:
                min = stock["weight"]

        return (max, min)

    def _normaliseWeights(self):
        max, min = self._getMaxMin()
        for stock in self.stocks:
            stock["normalised_weight"] = (stock["weight"] - min) / (max - min)

    def _updateStocks(self, new_prices):
        self._calculateWeights(new_prices)
        self._normaliseWeights()
        self.portfolio.updateAllStocks(new_prices)

    def _unboundedKnapsackRecurs(self, i):
        if i == 0:
            count = self.budget // self.stocks[0]["weight"]
            return (count * self.stocks[0]["price"], [self.stocks[0]["ticker"]] * count)

        not_take_val, not_take_items = self._unboundedKnapsackRecurs(self.budget, i - 1)

        take_val = float("-inf")
        take_items = list()

        if self.stocks[i]["weight"] <= self.budget:
            take_val_recurs, take_items_recurs = self._unboundedKnapsackRecurs(
                self.budget - self.stocks[i]["weight"], i
            )
            take_val = self.stocks[i]["price"] + take_val_recurs
            take_items = [self.stocks[i]["ticker"]] + take_items_recurs

            if take_val > not_take_val:
                return (take_val, take_items)
            else:
                return (not_take_val, not_take_items)

    def _cleanKnapsackValues(self, knapsack_stocks):
        portfolio = dict()
        for stock in knapsack_stocks:
            if stock in portfolio:
                portfolio[stock]["quantity"] += 1
            else:
                portfolio[stock] = {"quantity": 1}

        return portfolio

    def unboundedKnapsack(self, new_prices):
        self._updateStocks(new_prices)

        n = len(self.stocks)
        value, items = _unboundedKnapsackRecurs(self.budget, n - 1)
        return _cleanKnapsackValues(items)


class API:
    def __init__(self, uri):
        import sqlite3

        self.conn = sqlite3.connect(uri)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def getTimestamps(self):
        self.cur.execute("SELECT DISTINCT s.epoch FROM stocks s;")
        timestamps = [i["epoch"] for i in self.cur.fetchall()]
        return timestamps

    def getStocks(self, timestamp):
        self.cur.execute(
            "SELECT s.ticker, s.price FROM stocks s WHERE s.epoch = ?", (timestamp,)
        )
        return self.cur.fetchall()


from collections import UserDict


class Portfolio(UserDict):
    def __init__(self, initial_prices):
        super().__init__({
            i["ticker"]: {"price": i["price"], "quantity": 0} for i in initial_prices
        })

        self._value = None

    def updateStock(self, stock, price):
        new_data = {"price": price, "quantity": self.data[stock]["quantity"]}
        self.data[stock] = new_data

        self._value = None

    def updateAllStocks(self, new_prices):
        new_prices = dict(new_prices)
        for stock in self.data:
            self.updateStock(stock, new_prices[stock])

    def getTickers(self):
        return self.data.keys()

    def value(self):
        if self._value == None:
            for stock, data in self.data.items():
                self._value += data["price"] * data["quantity"]

        return self._value



class Account:
    def __init__(self, cash, budget_allocation, portfolio):
        self.initial_balance = cash
        self.cash = cash
        self.budget_allocation = budget_allocation
        self._generate_budget()
        self.portfolio = portfolio

    def _generate_budget(self):
        self.budget = self.cash * self.budget_allocation

    def _deposit(self, cash):
        self.cash += cash
        self._generate_budget()

    def _withdraw(self, cash):
        if self.cash - cash < 0:
            raise Exception(f"Trying to withdraw {cash} out of balance: {self.cash}")

        self.cash -= cash
        self._generate_budget()

    def sellStock(self, stock, quantity):
        sell_price = quantity * self.portfolio[stock]["price"]
        self.portfolio[stock]["quantity"] -= quantity
        self._deposit(sell_price)

    def buyStock(self, stock, quantity):
        buy_price = quantity * self.portfolio[stock]["price"]
        self.portfolio[stock]["quantity"] += quantity
        self._withdraw(buy_price)

    def updatePortfolioWithTemplate(self, template):
        for portfolio in self.portfolio:
            portfolio_quantity = portfolio["quantity"]

            if portfolio in template:
                template_quantity = template["quantity"]

                if portfolio_quantity > template_quantity:
                    self.sellStock(portfolio, portfolio_quantity - template_quantity)
                elif portfolio_quantity < template_quantity:
                    self.buyStock(portfolio, template_quantity - portfolio_quantity)
            elif portfolio_quantity > 0:
                self.sellStock(portfolio, portfolio_quantity)

    def value(self):
        return (self.cash + self.portfolio.value()) - self.initial_balance


if __name__ == "__main__":
    # Get access to data
    # api = API("../historic_data.db")
    api = API("../test.db")

    # Initalise timestamps
    timestamps = api.getTimestamps()

    # Initalise Portfolio and Bank
    bank = [Account(10_000, 0.1, Portfolio(api.getStocks(timestamps[0])))]

    # Loop through each account in bank account
    for account in bank:
        # Loop through each timestamp
        for timestamp in timestamps[1:]:
            # Initalise trading algorithm
            trading_algorithm = TradingAlgorithm(account)

            # Update all stocks in portfolio and run trading algorithm
            new_stocks = api.getStocks(timestamp)
            optimal_portfolio = trading_algorithm.unboundedKnapsack(new_stocks)
            
            # Update portfolio with new optimal portfolio
            account.portfolio.updatePortfolioWithTemplate(optimal_portfolio)

    # Print Summary
    print(f"""Trading Simulation Summary:
    - Initial balance: {account.initial_balance}
    - Budget Allocation: {account.budget_allocation}
    - Final balance: {account.cash}
    - Portfolio Value: {portfolio.value()}
    - Net Profit / Loss {account.value()}
    """)
