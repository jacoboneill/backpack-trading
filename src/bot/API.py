from stock import Stock
from portfolio import Portfolio

class API:
    def __init__(self, uri):
        import sqlite3

        self.conn = sqlite3.connect(uri)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.timestamps = self._getTimestamps()

    def _getTimestamps(self):
        self.cur.execute("SELECT DISTINCT s.epoch FROM stocks s ORDER BY s.epoch;")
        timestamps = [i["epoch"] for i in self.cur.fetchall()]
        return timestamps

    def getStocks(self, timestamp, sleep=0):
        self.cur.execute(
            "SELECT s.ticker, ROUND(s.price, 2) AS price FROM stocks s WHERE s.epoch = ?", (timestamp,)
        )
        return self._convertStocksToPortfolio(self.cur.fetchall())

    def _convertStocksToPortfolio(self, stocks):
        portfolio = Portfolio()
        for stock in stocks:
            portfolio.addStock(Stock(stock["ticker"], stock["price"]))

        return portfolio
