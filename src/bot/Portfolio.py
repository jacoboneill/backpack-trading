from collections import UserDict


class Portfolio(UserDict):
    def __init__(self, initial_prices):
        super().__init__(
            {i["ticker"]: {"price": i["price"], "quantity": 0} for i in initial_prices}
        )

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
